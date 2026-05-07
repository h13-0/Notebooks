#!/usr/bin/env python3
"""
AI Review CLI.

This implementation is intentionally dependency-light. It uses the Python
standard library for all runtime behavior and optionally uses PyYAML when it is
available for richer YAML parsing.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

from ai_review_lib.model_client import (
    call_model_with_retry,
)
from ai_review_lib.path_filter import configured_excludes, is_path_excluded


SEVERITY_ORDER = ["Enhance", "Minor", "Major", "Critical", "Unknown"]
ISSUE_SEVERITIES = set(SEVERITY_ORDER)
ISSUE_STATUS_DIRS = ["Open", "Closed", "PendingVote", "Rejected", "Superseded"]
STATUS_DIRS = {
    "open": "Open",
    "closed": "Closed",
    "pendingvote": "PendingVote",
    "pending_vote": "PendingVote",
    "rejected": "Rejected",
    "superseded": "Superseded",
}
AI_BLOCK_RE = re.compile(
    r"(?ms)^<!-- ai-review:start unit=ru[0-9]{6} -->.*?^<!-- ai-review:end -->\s*"
)
SUSPICIOUS_ENCODING_RE = re.compile(r"\?{4,}|\ufffd")
# Markdown ATX headings require whitespace after the opening # run.
# Obsidian tags such as #label must stay inside the current ReviewUnit.
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$")
WIKI_LINK_RE = re.compile(r"!?\[\[([^\]]+)\]\]")
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")
TAG_RE = re.compile(r"(?<!\w)#([\w\-\u4e00-\u9fff/]+)")
USER_NOTES_RE = re.compile(
    r"(?ms)<!-- user-notes:start -->.*?<!-- user-notes:end -->"
)
MAINTENANCE_CONTRACT_FILES = [
    "AI-Review/DESIGN.md",
    "AI-Review/IMPLEMENTATION.md",
    "AI-Review/MODEL_PROTOCOL.md",
    "skills/ai-review/SKILL.md",
    ".codex/skills/ai-review/SKILL.md",
    "tools/ai-review/README.md",
]


class AiReviewError(RuntimeError):
    pass


def now_date() -> str:
    return _dt.datetime.now().date().isoformat()


def print_info(message: str) -> None:
    print(f"[ai-review] {message}")


def print_warning(message: str) -> None:
    print(f"[ai-review][warning] {message}", file=sys.stderr)


def run_git(args: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise AiReviewError(proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed")
    return proc


def is_git_repo(root: Path) -> bool:
    return run_git(["rev-parse", "--is-inside-work-tree"], root).stdout.strip() == "true"


def git_head(root: Path) -> str:
    proc = run_git(["rev-parse", "HEAD"], root)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(load_text(path))
    except json.JSONDecodeError as exc:
        raise AiReviewError(f"状态文件 JSON 损坏：{path}: {exc}") from exc


def write_json_atomic(path: Path, data: Any) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if SUSPICIOUS_ENCODING_RE.search(text):
        raise AiReviewError(
            f"拒绝写入疑似编码损坏的 JSON：{path}。"
            "检测到连续问号或 Unicode 替换字符，请检查生成脚本/终端编码。"
        )
    write_text_atomic(path, text)


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value.split("  #", 1)[0].strip()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = load_text(path)
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data or {}
    except Exception:
        return parse_simple_yaml(text)


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    lines = text.splitlines()

    def next_content_line(start: int) -> tuple[int, str] | None:
        for next_raw in lines[start:]:
            if not next_raw.strip() or next_raw.lstrip().startswith("#"):
                continue
            return len(next_raw) - len(next_raw.lstrip(" ")), next_raw.strip()
        return None

    for index, raw in enumerate(lines):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            item_text = line[2:].strip()
            if not isinstance(parent, list):
                raise AiReviewError("简易 YAML 解析失败：列表缩进不合法")
            if ":" in item_text and not item_text.startswith('"'):
                key, val = item_text.split(":", 1)
                item: dict[str, Any] = {}
                if val.strip():
                    item[key.strip()] = parse_scalar(val)
                else:
                    next_line = next_content_line(index + 1)
                    item[key.strip()] = [] if next_line and next_line[0] > indent and next_line[1].startswith("- ") else {}
                parent.append(item)
                stack.append((indent, item))
            else:
                parent.append(parse_scalar(item_text))
            continue
        if ":" not in line:
            raise AiReviewError(f"简易 YAML 解析失败：缺少键值分隔符：{line}")
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if not isinstance(parent, dict):
            raise AiReviewError("简易 YAML 解析失败：映射缩进不合法")
        if val == "":
            next_line = next_content_line(index + 1)
            next_container: Any = [] if next_line and next_line[0] > indent and next_line[1].startswith("- ") else {}
            parent[key] = next_container
            stack.append((indent, next_container))
        else:
            parent[key] = parse_scalar(val)
    return root


def deep_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
    cur: Any = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def ensure_review_dirs(root: Path, review_dir: Path) -> None:
    for rel in [*ISSUE_STATUS_DIRS, ".state", ".tmp", ".cache"]:
        (review_dir / rel).mkdir(parents=True, exist_ok=True)
    for rel in [f"{status}/.gitkeep" for status in ISSUE_STATUS_DIRS]:
        p = review_dir / rel
        if not p.exists():
            p.write_text("", encoding="utf-8")


@dataclasses.dataclass
class ReviewUnit:
    unit_id: str
    file_path: Path
    rel_path: str
    heading_path: list[str]
    heading: str
    level: int
    content: str
    normalized: str
    content_hash: str
    start_line: int
    end_line: int
    requires_multimodal: bool = False
    attachments: list[str] = dataclasses.field(default_factory=list)
    outlinks: list[str] = dataclasses.field(default_factory=list)
    tags: list[str] = dataclasses.field(default_factory=list)
    existing_unit_id: str | None = None
    identity_block: "AiReviewBlock | None" = None


@dataclasses.dataclass
class AiReviewBlock:
    unit_id: str
    text: str
    anchor_line: int
    start_line: int
    end_line: int


@dataclasses.dataclass
class Finding:
    finding_id: str
    unit_id: str
    severity: str
    confidence: float
    title: str
    topic: list[str]
    summary: str
    evidence: list[str]
    suggested_fix: str
    requires_multimodal: bool
    context_used: list[str]
    external_sources: list[str]

    @classmethod
    def from_json(cls, payload: dict[str, Any], unit_id: str, index: int) -> "Finding":
        severity = str(payload.get("severity") or "Unknown")
        if severity not in SEVERITY_ORDER:
            severity = "Unknown"
        confidence = clamp_confidence(payload.get("confidence", 0.0))
        topic = as_string_list(payload.get("topic"))[:8]
        evidence = as_string_list(payload.get("evidence"))[:8]
        context_used = as_string_list(payload.get("context_used")) or ["current_unit"]
        external_sources = as_string_list(payload.get("external_sources"))[:12]
        finding_id = str(payload.get("finding_id") or f"{unit_id}-f{index:03d}")
        return cls(
            finding_id=finding_id,
            unit_id=str(payload.get("unit_id") or unit_id),
            severity=severity,
            confidence=confidence,
            title=str(payload.get("title") or "未命名问题"),
            topic=topic or ["未分类"],
            summary=str(payload.get("summary") or ""),
            evidence=evidence,
            suggested_fix=str(payload.get("suggested_fix") or ""),
            requires_multimodal=bool(payload.get("requires_multimodal", False)),
            context_used=[str(x) for x in context_used],
            external_sources=external_sources,
        )


@dataclasses.dataclass
class FindingVote:
    finding_id: str
    model_id: str
    model_role: str
    display_name: str
    decision: str
    confidence: float
    weight: float
    score: float
    rationale: str
    evidence: list[str]
    external_sources: list[str]

    @classmethod
    def from_json(cls, payload: dict[str, Any], model: dict[str, Any]) -> "FindingVote":
        decision = str(payload.get("decision") or "skip").lower()
        if decision not in {"support", "oppose", "skip"}:
            decision = "skip"
        confidence = clamp_confidence(payload.get("confidence", 0.0))
        weight = float(model.get("weight", 1))
        sign = 1 if decision == "support" else (-1 if decision == "oppose" else 0)
        return cls(
            finding_id=str(payload.get("finding_id") or ""),
            model_id=str(payload.get("model_id") or model.get("id") or "unknown-model"),
            model_role=str(payload.get("model_role") or model.get("role") or "voter"),
            display_name=str(model.get("display_name") or model.get("id") or payload.get("model_id") or "unknown-model"),
            decision=decision,
            confidence=confidence,
            weight=weight,
            score=sign * weight * confidence,
            rationale=str(payload.get("rationale") or ""),
            evidence=as_string_list(payload.get("evidence"))[:8],
            external_sources=as_string_list(payload.get("external_sources"))[:12],
        )


@dataclasses.dataclass
class FindingAggregate:
    finding: Finding
    status: str
    score: float
    score_threshold: float
    missing_vote_ratio: float
    support_votes: list[FindingVote]
    oppose_votes: list[FindingVote]
    skip_votes: list[FindingVote]
    missing_models: list[str]
    failed_models: list[str]
    eligible_models: list[str]
    all_votes: list[FindingVote]


def clamp_confidence(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.0


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]


def normalize_unit_text(text: str) -> str:
    text = AI_BLOCK_RE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_obsidian_target(raw: str) -> tuple[str, str, str]:
    """Split `path#fragment|alias` into parts."""
    no_alias, _, alias = raw.partition("|")
    path_part, _, fragment = no_alias.partition("#")
    return path_part.strip(), fragment.strip(), alias.strip()


def candidate_note_paths(root: Path, source_file: Path, target: str) -> list[Path]:
    target = target.replace("\\", "/").strip()
    if not target:
        return []
    p = Path(target)
    candidates: list[Path] = []
    if p.suffix:
        candidates.extend([(source_file.parent / p).resolve(), (root / p).resolve()])
    else:
        candidates.extend([(source_file.parent / f"{target}.md").resolve(), (root / f"{target}.md").resolve()])
    return candidates


def find_existing_candidate(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file():
            return path
    return None


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def slugify_title(text: str, max_len: int = 36) -> str:
    text = re.sub(r"[\\/:*?\"<>|#\[\]`]", "", text).strip()
    text = re.sub(r"\s+", "-", text)
    return (text[:max_len] or "未命名问题")


def list_markdown_files(root: Path, review_dir: Path, scope: str, paths: list[str]) -> list[Path]:
    config = load_yaml(root / ".ai-review.yaml")
    excluded_parts, excluded_globs = configured_excludes(config, review_dir, root)

    def allowed(path: Path) -> bool:
        if path.suffix.lower() != ".md":
            return False
        # 中文说明：扫描黑名单必须在最早阶段生效，避免 AI Review
        # 自身产物、skill、命令模板等 AI 生成文件参与普通笔记审查。
        if is_path_excluded(path, root, excluded_parts, excluded_globs):
            return False
        return True

    if paths:
        result: list[Path] = []
        for item in paths:
            p = (root / item).resolve()
            if p.is_file() and allowed(p):
                result.append(p)
            elif p.is_dir():
                result.extend(x for x in p.rglob("*.md") if allowed(x))
        return sorted(set(result))

    if scope == "changed":
        proc = run_git(["status", "--porcelain=v1", "--untracked-files=all"], root)
        changed: list[Path] = []
        for line in proc.stdout.splitlines():
            if not line:
                continue
            raw = line[3:].strip()
            if " -> " in raw:
                raw = raw.split(" -> ", 1)[1]
            raw = raw.strip('"')
            p = (root / raw).resolve()
            if p.exists() and allowed(p):
                changed.append(p)
        return sorted(set(changed))

    return sorted(p for p in root.rglob("*.md") if allowed(p))


def detect_existing_unit_id(text: str) -> str | None:
    match = re.search(r"<!-- ai-review:start unit=(ru[0-9]{6}) -->", text)
    return match.group(1) if match else None


def existing_ai_blocks_by_unit(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for block in collect_ai_blocks(text):
        blocks.setdefault(block.unit_id, block.text)
    return blocks


def collect_ai_blocks(text: str) -> list[AiReviewBlock]:
    blocks: list[AiReviewBlock] = []
    kept_lines = 0
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        start_match = re.match(r"<!-- ai-review:start unit=(ru[0-9]{6}) -->", line)
        if not start_match:
            kept_lines += 1
            index += 1
            continue
        start_line = index + 1
        block_lines = [line]
        index += 1
        while index < len(lines):
            block_lines.append(lines[index])
            if lines[index].strip() == "<!-- ai-review:end -->":
                index += 1
                break
            index += 1
        blocks.append(
            AiReviewBlock(
                unit_id=start_match.group(1),
                text="\n".join(block_lines).rstrip() + "\n",
                anchor_line=kept_lines,
                start_line=start_line,
                end_line=index,
            )
        )
    return blocks


def strip_ai_blocks_with_map(text: str) -> tuple[str, list[int], list[AiReviewBlock]]:
    cleaned: list[str] = []
    clean_to_original: list[int] = []
    blocks: list[AiReviewBlock] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        start_match = re.match(r"<!-- ai-review:start unit=(ru[0-9]{6}) -->", line)
        if not start_match:
            cleaned.append(line)
            clean_to_original.append(index + 1)
            index += 1
            continue
        start_line = index + 1
        block_lines = [line]
        index += 1
        while index < len(lines):
            block_lines.append(lines[index])
            if lines[index].strip() == "<!-- ai-review:end -->":
                index += 1
                break
            index += 1
        blocks.append(
            AiReviewBlock(
                unit_id=start_match.group(1),
                text="\n".join(block_lines).rstrip() + "\n",
                anchor_line=len(cleaned),
                start_line=start_line,
                end_line=index,
            )
        )
    return "\n".join(cleaned), clean_to_original, blocks


def find_block_for_range(blocks: list[AiReviewBlock], start_line: int, end_line: int) -> AiReviewBlock | None:
    candidates = [block for block in blocks if start_line <= block.anchor_line <= end_line + 1]
    return candidates[-1] if candidates else None


def locator_matches(entry: Any, rel_path: str, heading_path: list[str]) -> bool:
    return (
        isinstance(entry, dict)
        and entry.get("file") == rel_path
        and entry.get("heading_path") == heading_path
        and isinstance(entry.get("unit_id"), str)
    )


def ledger_unit_ids(unit_ledger: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for entry in unit_ledger.get("by_locator", {}).values():
        if isinstance(entry, dict) and isinstance(entry.get("unit_id"), str):
            ids.add(entry["unit_id"])
    return ids


def next_unique_unit_id(unit_ledger: dict[str, Any], claimed_ids: dict[str, str]) -> str:
    used = ledger_unit_ids(unit_ledger) | set(claimed_ids)
    next_id = int(unit_ledger.get("next_unit_id", 1))
    while True:
        unit_id = f"ru{next_id:06d}"
        next_id += 1
        if unit_id not in used:
            unit_ledger["next_unit_id"] = next_id
            return unit_id


def claimable_unit_id(unit_id: str | None, locator: str, claimed_ids: dict[str, str]) -> bool:
    if not unit_id:
        return False
    owner = claimed_ids.get(unit_id)
    return owner is None or owner == locator


def remember_hash_unit(by_hash: dict[str, Any], content_hash: str, unit_id: str) -> None:
    value = by_hash.get(content_hash)
    if isinstance(value, list):
        if unit_id not in value:
            value.append(unit_id)
        return
    if isinstance(value, str):
        by_hash[content_hash] = [value] if value == unit_id else [value, unit_id]
        return
    by_hash[content_hash] = [unit_id]


def duplicate_existing_blocks(files: list[Path], root: Path) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for path in files:
        rel = path.relative_to(root).as_posix()
        for block in collect_ai_blocks(load_text(path)):
            seen.setdefault(block.unit_id, []).append(f"{rel}:{block.start_line}")
    return {unit_id: locs for unit_id, locs in seen.items() if len(locs) > 1}


def split_units(
    path: Path,
    root: Path,
    unit_ledger: dict[str, Any],
    claimed_ids: dict[str, str] | None = None,
) -> list[ReviewUnit]:
    original = load_text(path)
    text, _clean_to_original, blocks = strip_ai_blocks_with_map(original)
    lines = text.splitlines()
    headings: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            headings.append((i, len(match.group(1)), match.group(2).strip()))
    ranges: list[tuple[int, int, int, str, list[str]]] = []
    if not headings:
        if normalize_unit_text(text):
            ranges.append((0, len(lines), 0, "_preamble", ["_preamble"]))
    else:
        if normalize_unit_text("\n".join(lines[: headings[0][0]])):
            ranges.append((0, headings[0][0], 0, "_preamble", ["_preamble"]))
        heading_stack: list[tuple[int, str]] = []
        for idx, (line_no, level, title) in enumerate(headings):
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
            end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
            chunk = "\n".join(lines[line_no:end])
            body = "\n".join(lines[line_no + 1 : end])
            if normalize_unit_text(body):
                ranges.append((line_no, end, level, title, [x[1] for x in heading_stack]))
    units: list[ReviewUnit] = []
    rel_path = path.relative_to(root).as_posix()
    by_locator = unit_ledger.setdefault("by_locator", {})
    by_hash = unit_ledger.setdefault("by_hash", {})
    claimed_ids = claimed_ids if claimed_ids is not None else {}
    for start, end, level, heading, heading_path in ranges:
        content = "\n".join(lines[start:end]).rstrip() + "\n"
        normalized = normalize_unit_text(content)
        content_hash = sha256_text(normalized)
        locator = f"{rel_path}::{' > '.join(heading_path)}"
        block = find_block_for_range(blocks, start + 1, end)
        existing_unit_id = block.unit_id if block else None
        locator_entry = by_locator.get(locator)
        locator_unit_id = locator_entry.get("unit_id") if locator_matches(locator_entry, rel_path, heading_path) else None
        if claimable_unit_id(existing_unit_id, locator, claimed_ids):
            unit_id = str(existing_unit_id)
        elif claimable_unit_id(locator_unit_id, locator, claimed_ids):
            unit_id = str(locator_unit_id)
        else:
            unit_id = next_unique_unit_id(unit_ledger, claimed_ids)
        claimed_ids[unit_id] = locator
        by_locator[locator] = {
            "unit_id": unit_id,
            "file": rel_path,
            "heading_path": heading_path,
            "content_hash": content_hash,
            "updated_at": now_date(),
        }
        remember_hash_unit(by_hash, content_hash, unit_id)
        outlinks = sorted(set(WIKI_LINK_RE.findall(content)))
        attachments = sorted(set(EMBED_RE.findall(content)))
        tags = sorted(set(TAG_RE.findall(content)))
        requires_multimodal = any(Path(a.split("#", 1)[0]).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"} for a in attachments)
        units.append(
            ReviewUnit(
                unit_id=unit_id,
                file_path=path,
                rel_path=rel_path,
                heading_path=heading_path,
                heading=heading,
                level=level,
                content=content,
                normalized=normalized,
                content_hash=content_hash,
                start_line=start + 1,
                end_line=end,
                requires_multimodal=requires_multimodal,
                attachments=attachments,
                outlinks=outlinks,
                tags=tags,
                existing_unit_id=existing_unit_id,
                identity_block=block,
            )
        )
    return units


def build_link_index(units: list[ReviewUnit]) -> dict[str, Any]:
    backlinks: dict[str, list[str]] = {}
    for unit in units:
        for target in unit.outlinks:
            backlinks.setdefault(target, []).append(f"{unit.rel_path}#{unit.unit_id}")
    return {"version": 1, "backlinks": backlinks, "updated_at": now_date()}


def extract_section_by_heading(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    level = 0
    for idx, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match and match.group(2).strip() == heading:
            start = idx
            level = len(match.group(1))
            break
    if start is None:
        return ""
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        match = HEADING_RE.match(lines[idx])
        if match and len(match.group(1)) <= level:
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def extract_section_from_heading_index(lines: list[str], start: int) -> str:
    match = HEADING_RE.match(lines[start])
    if not match:
        return ""
    level = len(match.group(1))
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        next_match = HEADING_RE.match(lines[idx])
        if next_match and len(next_match.group(1)) <= level:
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def extract_block_by_id(text: str, block_id: str) -> str:
    lines = text.splitlines()
    marker = f"^{block_id}"
    hit = next((idx for idx, line in enumerate(lines) if marker in line), None)
    if hit is None:
        return ""
    heading_match = HEADING_RE.match(lines[hit].replace(marker, "").strip())
    if heading_match:
        return extract_section_from_heading_index(lines, hit).replace(marker, "").strip()
    start = hit
    while start > 0 and lines[start - 1].strip() and not HEADING_RE.match(lines[start - 1]):
        start -= 1
    end = hit + 1
    while end < len(lines) and lines[end].strip() and not HEADING_RE.match(lines[end]):
        end += 1
    return "\n".join(lines[start:end]).replace(marker, "").strip()


def extract_outlink_context(root: Path, unit: ReviewUnit, config: dict[str, Any], warnings: set[str]) -> list[str]:
    if not deep_get(config, "context.include_outlinks", True) or not deep_get(config, "context.include_outlink_blocks", True):
        return []
    max_chars = int(deep_get(config, "context.max_outlink_chars", 2500))
    notes: list[str] = []
    for raw in unit.outlinks[: int(deep_get(config, "context.max_outlinks", 8))]:
        target, fragment, _alias = split_obsidian_target(raw)
        path = find_existing_candidate(candidate_note_paths(root, unit.file_path, target))
        if not path:
            continue
        text = AI_BLOCK_RE.sub("", load_text(path))
        excerpt = ""
        if fragment.startswith("^"):
            excerpt = extract_block_by_id(text, fragment[1:])
        elif fragment:
            excerpt = extract_section_by_heading(text, fragment)
        if not excerpt:
            continue
        rel = path.relative_to(root).as_posix()
        clipped = excerpt[:max_chars]
        suffix = "\n..." if len(excerpt) > max_chars else ""
        notes.append(f"Obsidian 引用上下文：[[{target}#{fragment}]]\n```markdown\n{clipped}{suffix}\n```")
    return notes


def build_context_notes(root: Path, unit: ReviewUnit, config: dict[str, Any], warnings: set[str]) -> list[str]:
    notes = extract_attachment_context(root, unit, config, warnings)
    notes.extend(extract_outlink_context(root, unit, config, warnings))
    return notes


def extract_attachment_context(root: Path, unit: ReviewUnit, config: dict[str, Any], warnings: set[str]) -> list[str]:
    notes: list[str] = []
    for attachment in unit.attachments:
        clean = attachment.split("#", 1)[0].split("|", 1)[0]
        suffix = Path(clean).suffix.lower()
        candidate = (unit.file_path.parent / clean).resolve()
        if not candidate.exists():
            candidate = (root / clean).resolve()
        if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            notes.append(f"图片附件：{attachment}")
        elif suffix == ".svg":
            notes.append(f"SVG 附件：{attachment}")
            if deep_get(config, "attachments.svg.convert_to_png", True):
                try:
                    import cairosvg  # type: ignore

                    cache = root / str(deep_get(config, "review_dir", "AI-Review")) / ".cache" / "svg"
                    cache.mkdir(parents=True, exist_ok=True)
                    out = cache / (hashlib.sha256(str(candidate).encode("utf-8")).hexdigest() + ".png")
                    cairosvg.svg2png(url=str(candidate), write_to=str(out))
                    notes.append(f"SVG 已临时转换 PNG：{out.relative_to(root).as_posix()}")
                except Exception:
                    key = "svg-convert-unavailable"
                    if key not in warnings:
                        warnings.add(key)
                        print_warning("SVG 转 PNG 需要 cairosvg；当前环境未启用，仍按 SVG 源码上下文审查。")
        elif suffix == ".zip" and candidate.exists():
            max_size = float(deep_get(config, "attachments.archive.max_size_mb", 5)) * 1024 * 1024
            max_files = int(deep_get(config, "attachments.archive.max_files", 50))
            if candidate.stat().st_size <= max_size:
                try:
                    with zipfile.ZipFile(candidate) as zf:
                        names = zf.namelist()[:max_files]
                    notes.append(f"ZIP 附件：{attachment}，文件：{', '.join(names[:10])}")
                except zipfile.BadZipFile:
                    notes.append(f"ZIP 附件无法打开：{attachment}")
        elif suffix in {".pdf", ".mp4", ".mov", ".mp3", ".wav"}:
            notes.append(f"暂不处理的附件类型：{attachment}")
    return notes


def build_prompt(unit: ReviewUnit, context_notes: list[str]) -> str:
    heading = " > ".join(unit.heading_path)
    return textwrap.dedent(
        f"""
        你是 AI Review 主模型。请只返回符合协议的 JSON，不要输出 Markdown。

        审查目标：
        - unit_id: {unit.unit_id}
        - source_file: {unit.rel_path}
        - heading_path: {heading}
        - content_hash: {unit.content_hash}

        要求：
        - 自然语言字段必须以简体中文为主。
        - 只审查当前 ReviewUnit，不要直接改写原文。
        - 输出必须包含 findings 数组；一个段落有多个独立问题时必须输出多个 finding。
        - 如果没有发现问题，findings 必须是空数组。
        - 每个 finding 的 finding_id 建议使用 {unit.unit_id}-f001、{unit.unit_id}-f002。
        - severity 只能是 Enhance/Minor/Major/Critical/Unknown。
        - topic 只用于 issue 和 Dashboard。
        - 如果依赖图片或多模态内容，finding.requires_multimodal 必须为 true。
        - 如果当前知识不足、事实可能过时，或需要核验权威资料，host-current 主模型必须联网查询。
        - prepare 阶段写入 task.external_sources 时，必须包含 URL/标题/用途以及可供外部 voter 离线判断的正文或关键摘录。
        - 联网查询时必须在 finding.external_sources 中列出 URL 或可追溯来源；summary/evidence 应明确哪些判断来自外部资料。

        附加上下文：
        {json.dumps(context_notes, ensure_ascii=False)}

        ReviewUnit 原文：
        ```markdown
        {unit.content}
        ```
        """
    ).strip()


def next_issue_id(issue_ledger: dict[str, Any]) -> str:
    value = str(issue_ledger.get("next_issue_id_hex", "0001"))
    number = int(value, 16)
    if number <= 0:
        number = 1
    issue_id = f"ar{number:04x}"
    issue_ledger["next_issue_id_hex"] = f"{number + 1:04x}"
    return issue_id


def source_block_ref(unit: ReviewUnit) -> str:
    return f"[[{unit.rel_path}#^{unit.unit_id}]]"


def issue_path(review_dir: Path, issue_id: str, status: str, severity: str, title: str) -> Path:
    status_dir = STATUS_DIRS.get(status.lower(), status)
    return review_dir / status_dir / f"{issue_id}-{severity}-{slugify_title(title)}.md"


def issue_move_target(review_dir: Path, src: Path, status: str) -> Path:
    target = review_dir / status / src.name
    if not target.exists():
        return target
    stem = src.stem
    suffix = src.suffix
    for idx in range(1, 1000):
        candidate = review_dir / status / f"{stem}-{idx}{suffix}"
        if not candidate.exists():
            return candidate
    raise AiReviewError(f"无法为 issue 移动生成唯一目标路径：{src}")


def update_issue_status_text(text: str, status: str) -> str:
    status_value = status.lower()
    text = re.sub(r"(?m)^status:\s*.*$", f"status: {status_value}", text, count=1)
    today = now_date()
    text = re.sub(r"(?m)^updated_at:\s*.*$", f"updated_at: {today}", text, count=1)
    marker = "## 复查记录\n\n"
    if marker in text:
        text = text.replace(marker, marker + f"- {today}：移动到 {status}。\n", 1)
    return text


def yaml_list(items: list[str], indent: int = 2) -> str:
    pad = " " * indent
    if not items:
        return f"{pad}[]"
    return "\n".join(f"{pad}- {json.dumps(item, ensure_ascii=False)}" for item in items)


def render_issue(unit: ReviewUnit, issue_id: str, aggregate: FindingAggregate, issue_file: Path, root: Path) -> str:
    today = now_date()
    head = git_head(root)
    finding = aggregate.finding
    status = aggregate.status.lower()
    topic_yaml = yaml_list(finding.topic, 2)
    heading_yaml = yaml_list(unit.heading_path, 2)
    models_supported = [v.model_id for v in aggregate.support_votes]
    models_disagreed = [v.model_id for v in aggregate.oppose_votes]
    models_skipped = [v.model_id for v in aggregate.skip_votes]
    models_missing = [*aggregate.missing_models, *aggregate.failed_models]
    votes_rows = []
    for v in aggregate.all_votes:
        votes_rows.append(
            f"| {v.display_name} | {v.model_role} | {v.decision} | {v.confidence:.2f} | {v.weight:g} | {v.score:.2f} | {v.rationale or '暂无。'} |"
        )
    evidence_items = list(finding.evidence)
    for vote in aggregate.all_votes:
        for item in vote.evidence:
            if item and item not in evidence_items:
                evidence_items.append(item)
    external_source_items = list(finding.external_sources)
    for vote in aggregate.all_votes:
        for item in vote.external_sources:
            if item and item not in external_source_items:
                external_source_items.append(item)
    evidence = "\n".join(f"- {x}" for x in evidence_items) if evidence_items else "暂无。"
    external_sources = "\n".join(f"- {x}" for x in external_source_items) if external_source_items else "暂无。"
    suggested = finding.suggested_fix or "暂无；AI Review 不直接修改原文正文。"
    return textwrap.dedent(
        f"""\
        ---
        id: {issue_id}
        status: {status}
        severity: {finding.severity}
        source_file: {json.dumps(unit.rel_path, ensure_ascii=False)}
        source_unit_id: {json.dumps(unit.unit_id, ensure_ascii=False)}
        source_finding_id: {json.dumps(finding.finding_id, ensure_ascii=False)}
        source_block_ref: {json.dumps(source_block_ref(unit), ensure_ascii=False)}
        source_heading_path:
        {heading_yaml}
        topic:
        {topic_yaml}
        created_at: {today}
        updated_at: {today}
        created_git_hash: {json.dumps(head)}
        updated_git_hash: {json.dumps(head)}
        content_hash: {json.dumps(unit.content_hash)}
        models_supported:
        {yaml_list(models_supported, 2)}
        models_disagreed:
        {yaml_list(models_disagreed, 2)}
        models_skipped:
        {yaml_list(models_skipped, 2)}
        models_missing:
        {yaml_list(models_missing, 2)}
        score: {aggregate.score:.4f}
        score_threshold: {aggregate.score_threshold:.4f}
        missing_vote_ratio: {aggregate.missing_vote_ratio:.4f}
        tags:
          - AI-Review
        ---

        # {finding.title} ^{issue_id}

        #AI-Review

        ## 原文位置

        - {source_block_ref(unit)}

        ## 问题等级

        {finding.severity}

        ## Topic

        {chr(10).join(f"- {x}" for x in finding.topic)}

        ## 问题摘要

        {finding.summary}

        ## 模型投票

        | 模型 | 角色 | 决策 | 置信度 | 权重 | 分数 | 理由 |
        |---|---|---|---:|---:|---:|---|
        {chr(10).join(votes_rows) if votes_rows else "| 无 | - | skip | 0.00 | 0 | 0.00 | 无可用投票 |"}

        ## 投票汇总

        - 支持模型：{", ".join(models_supported) if models_supported else "无"}
        - 反对模型：{", ".join(models_disagreed) if models_disagreed else "无"}
        - 跳过模型：{", ".join(models_skipped) if models_skipped else "无"}
        - 缺失/失败模型：{", ".join(models_missing) if models_missing else "无"}
        - 总分：{aggregate.score:.2f}
        - 合入阈值：{aggregate.score_threshold:.2f}
        - 缺失/失败比例：{aggregate.missing_vote_ratio:.2f}

        ## 具体问题

        {evidence}

        ## 外部来源

        {external_sources}

        ## 建议修改

        {suggested}

        ## 复查记录

        - {today}：创建。

        ## 人工备注

        <!-- user-notes:start -->

        <!-- user-notes:end -->
        """
    )


def render_ai_block(unit: ReviewUnit, issues: list[tuple[str, Path]], model_names: list[str]) -> str:
    callout = "bug" if issues else "success"
    lines = [f"<!-- ai-review:start unit={unit.unit_id} -->", f"> [!{callout}]- AI Review `{unit.unit_id}`"]
    if issues:
        for issue_id, path in issues:
            link = path.with_suffix("").as_posix()
            lines.append(f"> - [ ] [[{link}|{issue_id}]]")
    else:
        lines.append("> - [[AI-Review/Dashboard|Dashboard]]")
    names = "/".join(model_names) if model_names else "无可用模型"
    lines.append(f"> `{now_date()}` · {names}")
    lines.append(f"^{unit.unit_id}")
    lines.append("<!-- ai-review:end -->")
    return "\n".join(lines) + "\n"


def render_identity_block(unit: ReviewUnit) -> str:
    lines = [
        f"<!-- ai-review:start unit={unit.unit_id} -->",
        f"> [!question]- AI Review `{unit.unit_id}`",
        "> - 待审查",
        f"> `{now_date()}` · identity",
        f"^{unit.unit_id}",
        "<!-- ai-review:end -->",
    ]
    return "\n".join(lines) + "\n"


def replace_identity_blocks_for_file(path: Path, units: list[ReviewUnit]) -> tuple[str, int]:
    original = load_text(path)
    _cleaned, clean_to_original, _blocks = strip_ai_blocks_with_map(original)
    lines = original.splitlines()
    inserts: dict[int, list[str]] = {}
    replacements: dict[int, tuple[int, str]] = {}
    created = 0
    for unit in units:
        if unit.identity_block and unit.existing_unit_id == unit.unit_id:
            continue
        block = render_identity_block(unit)
        if unit.identity_block and unit.existing_unit_id != unit.unit_id:
            replacements[unit.identity_block.start_line] = (unit.identity_block.end_line, block)
        else:
            original_line = clean_to_original[unit.end_line - 1] if 0 < unit.end_line <= len(clean_to_original) else len(lines)
            inserts.setdefault(original_line, []).append(block)
            created += 1
    out: list[str] = []
    idx = 1
    while idx <= len(lines):
        if idx in replacements:
            end_line, block = replacements[idx]
            if out and out[-1].strip():
                out.append("")
            out.extend(block.rstrip().splitlines())
            out.append("")
            idx = end_line + 1
            continue
        line = lines[idx - 1]
        out.append(line)
        if idx in inserts:
            for block in inserts[idx]:
                if out and out[-1].strip():
                    out.append("")
                out.extend(block.rstrip().splitlines())
                out.append("")
        idx += 1
    if 0 in inserts or not lines:
        for block in inserts.get(0, []):
            if out and out[-1].strip():
                out.append("")
            out.extend(block.rstrip().splitlines())
            out.append("")
    return "\n".join(out).rstrip() + "\n", created


def replace_ai_blocks_for_file(path: Path, units: list[ReviewUnit], aggregates: dict[str, Any], issue_links: dict[str, list[tuple[str, Path]]]) -> str:
    text = AI_BLOCK_RE.sub("", load_text(path)).rstrip() + "\n"
    lines = text.splitlines()
    inserts: dict[int, str] = {}
    for unit in units:
        inserts[unit.end_line] = render_ai_block(unit, issue_links.get(unit.unit_id, []), [])
    out: list[str] = []
    for idx, line in enumerate(lines, start=1):
        out.append(line)
        if idx in inserts:
            if out and out[-1].strip():
                out.append("")
            out.extend(inserts[idx].rstrip().splitlines())
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def collect_issues(review_dir: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for status_dir in ISSUE_STATUS_DIRS:
        for path in (review_dir / status_dir).glob("*.md"):
            text = load_text(path)
            meta = parse_frontmatter(text)
            issue_id = meta.get("id") or path.stem.split("-", 1)[0]
            topic_match = re.search(r"(?ms)^## Topic\s*(.*?)(?:\n## |\Z)", text)
            topics = re.findall(r"^- (.+)$", topic_match.group(1), re.M) if topic_match else []
            items.append(
                {
                    "id": issue_id,
                    "path": path,
                    "status": status_dir,
                    "severity": meta.get("severity", "Unknown"),
                    "source_file": meta.get("source_file", ""),
                    "source_unit_id": meta.get("source_unit_id", ""),
                    "source_finding_id": meta.get("source_finding_id", ""),
                    "title": re.search(r"^# (.+?)(?: \^ar[0-9a-f]+)?$", text, re.M).group(1)
                    if re.search(r"^# (.+?)(?: \^ar[0-9a-f]+)?$", text, re.M)
                    else path.stem,
                    "topic": topics,
                }
            )
    return sorted(items, key=lambda x: x["id"])


def render_dashboard(review_dir: Path, top_n: int) -> str:
    issues = collect_issues(review_dir)
    counts = {status: 0 for status in ISSUE_STATUS_DIRS}
    for item in issues:
        counts[item["status"]] += 1
    open_like = [x for x in issues if x["status"] in {"Open", "PendingVote"}]
    sev_rank = {"Critical": 5, "Major": 4, "Minor": 3, "Enhance": 2, "Unknown": 1, "Correct": 0}
    open_like.sort(key=lambda x: (sev_rank.get(x["severity"], 0), x["id"]), reverse=True)
    top_lines = []
    for item in open_like[:top_n]:
        link = item["path"].with_suffix("").as_posix()
        top_lines.append(f"- [[{link}|{item['id']}]] · {item['severity']} · {item['title']}")
    topic_map: dict[str, list[dict[str, Any]]] = {}
    for item in issues:
        for topic in item["topic"] or ["未分类"]:
            topic_map.setdefault(topic, []).append(item)
    topic_lines = []
    for topic, vals in sorted(topic_map.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        topic_lines.append(f"- {topic}：{len(vals)}")
    pending_lines = []
    for item in [x for x in issues if x["status"] == "PendingVote"][:top_n]:
        link = item["path"].with_suffix("").as_posix()
        pending_lines.append(f"- [[{link}|{item['id']}]] · {item['title']}")
    return textwrap.dedent(
        f"""\
        # AI Review Dashboard

        #AI-Review

        > 本文件由 AI Review 自动维护。人工可阅读，但不建议手动编辑自动生成区域。

        ## 总览

        | 状态 | 数量 |
        |---|---:|
        | Open | {counts['Open']} |
        | Closed | {counts['Closed']} |
        | PendingVote | {counts['PendingVote']} |
        | Rejected | {counts['Rejected']} |
        | Superseded | {counts['Superseded']} |

        ## 当前最重要问题 Top N

        {chr(10).join(top_lines) if top_lines else "暂无。"}

        ## 按 Topic 聚合

        {chr(10).join(topic_lines) if topic_lines else "暂无。"}

        ## 已勾选但复查失败

        暂无。

        ## PendingVote / 待投票

        {chr(10).join(pending_lines) if pending_lines else "暂无。"}
        """
    )


def validate_issue_notes(review_dir: Path) -> None:
    for issue in collect_issues(review_dir):
        text = load_text(issue["path"])
        starts = text.count("<!-- user-notes:start -->")
        ends = text.count("<!-- user-notes:end -->")
        if starts != 1 or ends != 1 or not USER_NOTES_RE.search(text):
            raise AiReviewError(f"人工备注区边界损坏，停止更新：{issue['path']}")


def validate_markdown_and_links(root: Path, files: Iterable[Path]) -> list[str]:
    warnings: list[str] = []
    for path in files:
        text = load_text(path)
        if text.count("```") % 2:
            warnings.append(f"代码块围栏数量疑似不匹配：{path.relative_to(root).as_posix()}")
        for link in WIKI_LINK_RE.findall(text):
            target, _fragment, _alias = split_obsidian_target(link)
            if not target or re.match(r"https?://", target):
                continue
            candidates = candidate_note_paths(root, path, target)
            if not any(c.exists() for c in candidates):
                warnings.append(f"Obsidian 链接目标未找到：{path.relative_to(root).as_posix()} -> {target}")
    return warnings


def git_preflight(root: Path, config: dict[str, Any], apply: bool) -> list[str]:
    warnings: list[str] = []
    if not is_git_repo(root):
        raise AiReviewError("当前目录不是 Git 仓库。")
    if not apply:
        return warnings
    if deep_get(config, "git.fetch_before_check", True):
        proc = run_git(["fetch", "--all", "--prune"], root)
        if proc.returncode != 0:
            raise AiReviewError(f"git fetch 失败：{proc.stderr.strip()}")
    if deep_get(config, "git.require_clean_worktree", True):
        proc = run_git(["status", "--porcelain"], root)
        submodule_rels = set(submodule_paths(root))
        allowed = []
        for line in proc.stdout.splitlines():
            if "AI-Review/.tmp/" in line or "AI-Review/.cache/" in line:
                continue
            raw = line[3:].strip()
            if " -> " in raw:
                raw = raw.split(" -> ", 1)[1]
            raw = raw.strip('"').replace("\\", "/")
            if raw in submodule_rels:
                continue
            allowed.append(line)
        if allowed:
            raise AiReviewError("写入前主仓库工作区或暂存区不干净。")
    if deep_get(config, "git.require_synced_with_upstream", True):
        upstream = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], root)
        if upstream.returncode != 0:
            raise AiReviewError("当前分支没有 upstream。")
        local = run_git(["rev-parse", "HEAD"], root, check=True).stdout.strip()
        remote = run_git(["rev-parse", "@{u}"], root, check=True).stdout.strip()
        if local != remote:
            raise AiReviewError("当前 HEAD 与 upstream 不同步。")
    warnings.extend(check_submodules(root, config, apply))
    return warnings


def submodule_paths(root: Path) -> list[str]:
    proc = run_git(["submodule", "status", "--recursive"], root)
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    result: list[str] = []
    for line in proc.stdout.splitlines():
        parts = line[1:].split()
        if len(parts) >= 2:
            result.append(parts[1].replace("\\", "/"))
    return result


def dirty_submodule_paths(root: Path, config: dict[str, Any], apply: bool) -> set[str]:
    dirty: set[str] = set()
    if not apply or not deep_get(config, "submodules.scan", True):
        return dirty
    proc = run_git(["submodule", "status", "--recursive"], root)
    if proc.returncode != 0 or not proc.stdout.strip():
        return dirty
    for line in proc.stdout.splitlines():
        state = line[:1]
        parts = line[1:].split()
        if len(parts) < 2:
            continue
        sha, rel = parts[0], parts[1].replace("\\", "/")
        sub = root / rel
        if state == "-" or not sub.exists():
            dirty.add(rel)
            continue
        if deep_get(config, "submodules.require_clean_worktree", True):
            st = run_git(["status", "--porcelain"], sub)
            if st.stdout.strip():
                dirty.add(rel)
                continue
        if deep_get(config, "submodules.skip_if_head_mismatch", True):
            head = run_git(["rev-parse", "HEAD"], sub)
            if head.returncode == 0 and head.stdout.strip() != sha:
                dirty.add(rel)
    return dirty


def is_under_repo_rel(path: Path, root: Path, rel: str) -> bool:
    path_rel = path.relative_to(root).as_posix()
    rel = rel.rstrip("/")
    return path_rel == rel or path_rel.startswith(rel + "/")


def check_submodules(root: Path, config: dict[str, Any], apply: bool) -> list[str]:
    warnings: list[str] = []
    if not deep_get(config, "submodules.scan", True):
        return warnings
    proc = run_git(["submodule", "status", "--recursive"], root)
    if proc.returncode != 0 or not proc.stdout.strip():
        return warnings
    for line in proc.stdout.splitlines():
        state = line[:1]
        parts = line[1:].split()
        if len(parts) < 2:
            continue
        sha, rel = parts[0], parts[1]
        sub = root / rel
        if state == "-" and deep_get(config, "submodules.skip_uninitialized", True):
            warnings.append(f"submodule 未初始化，跳过：{rel}")
            continue
        if not sub.exists():
            warnings.append(f"submodule 路径不存在，跳过：{rel}")
            continue
        if apply and deep_get(config, "submodules.require_clean_worktree", True):
            st = run_git(["status", "--porcelain"], sub)
            if st.stdout.strip():
                warnings.append(f"submodule dirty，跳过：{rel}")
        if apply and deep_get(config, "submodules.skip_if_head_mismatch", True):
            head = run_git(["rev-parse", "HEAD"], sub)
            if head.returncode == 0 and head.stdout.strip() != sha:
                warnings.append(f"submodule HEAD 与主仓库记录不一致，跳过：{rel}")
    return warnings


def save_run_state(review_dir: Path, state: dict[str, Any]) -> None:
    write_json_atomic(review_dir / ".state" / "run-state.json", state)


class VoteStatusBoard:
    """Small multi-model status display for `ai-review vote`.

    中文说明：每个活跃任务占一行。流式内容只展示最后一小段，
    前面用省略号压缩，避免模型输出刷满终端。
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._rows: dict[str, dict[str, Any]] = {}
        self._last_render = 0.0
        self._printed_lines = 0
        self._interactive = sys.stdout.isatty()

    def update(self, key: str, **fields: Any) -> None:
        with self._lock:
            row = self._rows.setdefault(key, {"started": time.monotonic(), "chars": 0, "preview": ""})
            row.update(fields)
            now = time.monotonic()
            if now - self._last_render >= 0.25 or fields.get("done"):
                self._last_render = now
                self._render_locked()

    def _render_locked(self) -> None:
        lines = ["[vote status]"]
        for key in sorted(self._rows):
            row = self._rows[key]
            elapsed = max(time.monotonic() - float(row.get("started", time.monotonic())), 0.01)
            chars = int(row.get("chars", 0))
            approx_tokens = max(chars // 4, int(row.get("tokens", 0) or 0))
            speed = approx_tokens / elapsed
            preview = str(row.get("preview", "")).replace("\n", " ").replace("\r", " ")
            if len(preview) > 64:
                preview = "..." + preview[-61:]
            status = row.get("status", "running")
            lines.append(f"- {key:<34} {status:<10} {elapsed:6.1f}s {speed:6.1f} tok/s {approx_tokens:5d} tok {preview}")
        if self._interactive and self._printed_lines:
            sys.stdout.write(f"\x1b[{self._printed_lines}F")
        for line in lines:
            prefix = "\x1b[2K" if self._interactive else ""
            sys.stdout.write(prefix + line[:160] + "\n")
        sys.stdout.flush()
        self._printed_lines = len(lines) if self._interactive else 0


def task_dirs(review_dir: Path) -> tuple[Path, Path]:
    tasks_dir = review_dir / ".state" / "tasks"
    votes_dir = review_dir / ".state" / "votes"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    votes_dir.mkdir(parents=True, exist_ok=True)
    return tasks_dir, votes_dir


def task_path(tasks_dir: Path, task_id: str) -> Path:
    return tasks_dir / f"{task_id}.json"


def vote_path(votes_dir: Path, model_id: str, task_id: str) -> Path:
    return votes_dir / model_id / f"{task_id}.json"


def task_to_unit(root: Path, task: dict[str, Any]) -> ReviewUnit:
    return ReviewUnit(
        unit_id=str(task["task_id"]),
        file_path=root / str(task["source_file"]),
        rel_path=str(task["source_file"]),
        heading_path=[str(x) for x in task.get("heading_path", [])],
        heading=str(task.get("heading") or ""),
        level=int(task.get("level") or 0),
        content=str(task.get("content") or ""),
        normalized=normalize_unit_text(str(task.get("content") or "")),
        content_hash=str(task.get("task_hash") or task.get("content_hash") or ""),
        start_line=int(task.get("start_line") or 0),
        end_line=int(task.get("end_line") or 0),
        requires_multimodal=bool(task.get("requires_multimodal", False)),
        attachments=[str(x) for x in task.get("attachments", [])],
        outlinks=[str(x) for x in task.get("outlinks", [])],
        tags=[str(x) for x in task.get("tags", [])],
    )


def normalize_task_payload(unit_payload: dict[str, Any]) -> dict[str, Any]:
    task = dict(unit_payload)
    task["task_id"] = task.get("task_id") or task.get("unit_id")
    task["task_hash"] = task.get("task_hash") or task.get("content_hash")
    task["unit_id"] = task["task_id"]
    task["content_hash"] = task["task_hash"]
    return task


def normalize_findings(payload: dict[str, Any], task: dict[str, Any]) -> list[Finding]:
    findings_raw = payload.get("findings") or []
    if not isinstance(findings_raw, list):
        raise AiReviewError(f"host-current vote 的 findings 必须是数组：{task['task_id']}")
    findings: list[Finding] = []
    for index, item in enumerate(findings_raw, start=1):
        if isinstance(item, dict):
            findings.append(Finding.from_json(item, str(task["task_id"]), index))
    return findings


def host_vote_path(votes_dir: Path, task_id: str) -> Path:
    return vote_path(votes_dir, "host-current", task_id)


def load_host_findings(votes_dir: Path, task: dict[str, Any]) -> list[Finding]:
    path = host_vote_path(votes_dir, str(task["task_id"]))
    if not path.exists():
        return []
    payload = load_json(path, {})
    if payload.get("task_hash") != task.get("task_hash"):
        return []
    return normalize_findings(payload, task)


def model_can_vote_finding(model: dict[str, Any], finding: Finding) -> bool:
    return not finding.requires_multimodal or bool(model.get("multimodal", False)) or str(model.get("id")) == "host-current"


def build_voter_prompt(task: dict[str, Any], findings: list[Finding]) -> str:
    findings_payload = [
        {
            "finding_id": finding.finding_id,
            "severity": finding.severity,
            "title": finding.title,
            "summary": finding.summary,
            "evidence": finding.evidence,
            "suggested_fix": finding.suggested_fix,
            "requires_multimodal": finding.requires_multimodal,
            "topic": finding.topic,
            "external_sources": finding.external_sources,
        }
        for finding in findings
    ]
    return textwrap.dedent(
        f"""
        你是 AI Review 外部 voter。请只返回符合协议的 JSON，不要输出 Markdown。

        任务：
        - task_id: {task['task_id']}
        - unit_id: {task['unit_id']}
        - task_hash: {task['task_hash']}
        - source_file: {task.get('source_file')}

        要求：
        - 只对给定 findings 投票，不要把新问题加入本轮 votes。
        - 每个 finding 必须返回一票，decision 只能是 support/oppose/skip。
        - support 表示支持该 bug 成立；oppose 表示反对该 bug 成立；skip 表示无投票权或无法判断。
        - confidence 必须是 0 到 1。
        - 自然语言字段必须以简体中文为主。
        - 不要假设当前 API 模型具备联网能力；如需外部资料，必须优先使用下方“prepare 阶段外部资料”中的 content/excerpt。

        输出格式：
        {{
          "task_id": "{task['task_id']}",
          "unit_id": "{task['unit_id']}",
          "task_hash": "{task['task_hash']}",
          "votes": [
            {{"finding_id": "...", "decision": "support", "confidence": 0.8, "rationale": "...", "evidence": [], "external_sources": []}}
          ],
          "new_findings_suggestion": []
        }}

        候选 findings：
        {json.dumps(findings_payload, ensure_ascii=False, indent=2)}

        附加上下文：
        {json.dumps(task.get("prepared_context") or task.get("context_notes") or [], ensure_ascii=False, indent=2)}

        prepare 阶段外部资料：
        {json.dumps(task.get("external_sources") or [], ensure_ascii=False, indent=2)}

        ReviewUnit 原文：
        ```markdown
        {task.get("content") or ""}
        ```
        """
    ).strip()


def normalize_vote_payload(payload: dict[str, Any], model: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    vote = dict(payload)
    vote["version"] = vote.get("version", 1)
    vote["task_id"] = vote.get("task_id") or vote.get("unit_id") or task["task_id"]
    vote["unit_id"] = vote["task_id"]
    vote["task_hash"] = vote.get("task_hash") or task["task_hash"]
    vote["content_hash"] = vote["task_hash"]
    vote["model_id"] = vote.get("model_id") or model.get("id")
    vote["model_role"] = vote.get("model_role") or "reviewer"
    normalized_votes = []
    raw_votes = vote.get("votes") or []
    if isinstance(raw_votes, dict):
        raw_votes = [raw_votes]
    if isinstance(raw_votes, list):
        for item in raw_votes:
            if not isinstance(item, dict):
                continue
            item = dict(item)
            item["model_id"] = vote["model_id"]
            item["model_role"] = vote["model_role"]
            normalized_votes.append(dataclasses.asdict(FindingVote.from_json(item, model)))
    vote["votes"] = normalized_votes
    vote["created_at"] = vote.get("created_at") or _dt.datetime.now().isoformat()
    return vote


def reviewer_models(config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    voters = [dict(x) for x in deep_get(config, "models.voters", []) or [] if x.get("vote_enabled", True)]
    if getattr(args, "model", None):
        voters = [x for x in voters if x.get("id") == args.model]
    voters = [x for x in voters if str(x.get("id")) != "host-current"]
    return voters


def validate_task_sources(root: Path, review_dir: Path, tasks: list[dict[str, Any]]) -> None:
    unit_ledger = load_json(review_dir / ".state" / "review-unit-ledger.json", {"version": 1, "next_unit_id": 1, "units": {}})
    units_by_file: dict[Path, dict[str, ReviewUnit]] = {}
    for task in tasks:
        source_file = root / str(task.get("source_file") or "")
        if not source_file.exists():
            raise AiReviewError(f"task 源文件不存在：{task.get('source_file')}")
        if source_file not in units_by_file:
            units_by_file[source_file] = {unit.unit_id: unit for unit in split_units(source_file, root, unit_ledger)}
        unit = units_by_file[source_file].get(str(task.get("task_id")))
        if not unit:
            raise AiReviewError(f"task 对应 ReviewUnit 不存在：{task.get('task_id')}")
        blocks = existing_ai_blocks_by_unit(load_text(source_file))
        if unit.unit_id not in blocks:
            raise AiReviewError(f"源文件缺少 identity 块：{task.get('source_file')} -> {unit.unit_id}")
        if unit.content_hash != task.get("task_hash"):
            raise AiReviewError(f"task 已过期：{task.get('task_id')} 当前 hash={unit.content_hash} task_hash={task.get('task_hash')}")


def configured_model_map(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    models = {str(m.get("id")): dict(m) for m in deep_get(config, "models.voters", []) or [] if m.get("vote_enabled", True)}
    main = dict(deep_get(config, "models.main", {}) or {})
    main.setdefault("id", "host-current")
    main.setdefault("role", "main")
    models[str(main.get("id"))] = main
    return models


def aggregate_finding(
    finding: Finding,
    task: dict[str, Any],
    votes_dir: Path,
    model_map: dict[str, dict[str, Any]],
    config: dict[str, Any],
) -> FindingAggregate:
    main_model = model_map.get("host-current", {"id": "host-current", "role": "main", "weight": 1, "display_name": "host-current"})
    main_vote = FindingVote(
        finding_id=finding.finding_id,
        model_id="host-current",
        model_role="main",
        display_name=str(main_model.get("display_name") or "host-current"),
        decision="support",
        confidence=finding.confidence,
        weight=float(main_model.get("weight", 1)),
        score=float(main_model.get("weight", 1)) * finding.confidence,
        rationale="主模型提出该 finding。",
        evidence=finding.evidence,
        external_sources=finding.external_sources,
    )
    support_votes = [main_vote]
    oppose_votes: list[FindingVote] = []
    skip_votes: list[FindingVote] = []
    missing_models: list[str] = []
    failed_models: list[str] = []
    eligible_models: list[str] = ["host-current"]

    for model_id, model in sorted(model_map.items()):
        if model_id == "host-current":
            continue
        if not model_can_vote_finding(model, finding):
            continue
        eligible_models.append(model_id)
        path = vote_path(votes_dir, model_id, str(task["task_id"]))
        if not path.exists():
            missing_models.append(model_id)
            continue
        payload = load_json(path, {})
        if payload.get("task_hash") != task.get("task_hash"):
            missing_models.append(model_id)
            continue
        raw_votes = payload.get("votes") or []
        if not isinstance(raw_votes, list):
            failed_models.append(model_id)
            continue
        matched = next((item for item in raw_votes if isinstance(item, dict) and item.get("finding_id") == finding.finding_id), None)
        if not matched:
            missing_models.append(model_id)
            continue
        vote = FindingVote.from_json({**matched, "model_id": model_id, "model_role": model.get("role", "voter")}, model)
        if vote.decision == "support":
            support_votes.append(vote)
        elif vote.decision == "oppose":
            oppose_votes.append(vote)
        else:
            skip_votes.append(vote)

    all_votes = [*support_votes, *oppose_votes, *skip_votes]
    score = sum(v.score for v in all_votes)
    eligible_count = max(len(eligible_models), 1)
    missing_ratio = (len(missing_models) + len(failed_models)) / eligible_count
    score_threshold = float(deep_get(config, "voting.issue_score_threshold", 3.0))
    missing_threshold = float(deep_get(config, "voting.max_missing_vote_ratio", 0.5))
    if missing_ratio > missing_threshold:
        status = "PendingVote"
    elif score >= score_threshold:
        status = "Open"
    else:
        status = "Rejected"
    return FindingAggregate(
        finding=finding,
        status=status,
        score=score,
        score_threshold=score_threshold,
        missing_vote_ratio=missing_ratio,
        support_votes=support_votes,
        oppose_votes=oppose_votes,
        skip_votes=skip_votes,
        missing_models=missing_models,
        failed_models=failed_models,
        eligible_models=eligible_models,
        all_votes=all_votes,
    )


def command_vote_tasks(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    secrets = load_yaml(root / ".ai-review-secrets.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    tasks_dir, votes_dir = task_dirs(review_dir)
    tasks = [load_json(p, {}) for p in sorted(tasks_dir.glob("*.json"))]
    if args.limit:
        tasks = tasks[: int(args.limit)]
    models = reviewer_models(config, args)
    if not models:
        raise AiReviewError("没有可运行的外部 reviewer。")

    timeout = int(args.model_timeout or deep_get(config, "runtime.request_timeout_sec", 300))
    retry = int(args.model_retry if args.model_retry is not None else deep_get(config, "runtime.retry", 0))
    stream = bool(deep_get(config, "runtime.stream", True))
    stream_total_timeout = int(args.stream_total_timeout or deep_get(config, "runtime.stream_total_timeout_sec", 1800))
    board = VoteStatusBoard()
    jobs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    skipped = 0
    for model in models:
        model_id = str(model.get("id"))
        for task in tasks:
            task = normalize_task_payload(task)
            findings = load_host_findings(votes_dir, task)
            if not findings:
                print_warning(f"{task['task_id']} 缺少有效 host-current findings，外部 voter 跳过。")
                continue
            out = vote_path(votes_dir, model_id, task["task_id"])
            old = load_json(out, None) if out.exists() else None
            if old and old.get("task_hash") == task.get("task_hash"):
                skipped += 1
                continue
            jobs.append((model, task))

    if getattr(args, "concurrency", None):
        per_model_concurrency = {str(model.get("id")): max(1, int(args.concurrency)) for model in models}
    else:
        per_model_concurrency = {
            str(model.get("id")): max(1, int(model.get("concurrency") or 1))
            for model in models
        }
    semaphores = {model_id: threading.Semaphore(limit) for model_id, limit in per_model_concurrency.items()}

    def run_one(model: dict[str, Any], task: dict[str, Any]) -> tuple[str, str]:
        model_id = str(model.get("id"))
        task_id = str(task["task_id"])
        key = f"{model_id}/{task_id}"
        board.update(key, status="running")
        findings = load_host_findings(votes_dir, task)
        eligible = [finding for finding in findings if model_can_vote_finding(model, finding)]
        skip_votes = [
            dataclasses.asdict(
                FindingVote(
                    finding_id=finding.finding_id,
                    model_id=model_id,
                    model_role=str(model.get("role") or "voter"),
                    display_name=str(model.get("display_name") or model_id),
                    decision="skip",
                    confidence=1.0,
                    weight=float(model.get("weight", 1)),
                    score=0.0,
                    rationale="该 finding 需要多模态能力，当前模型无投票权。",
                    evidence=[],
                    external_sources=[],
                )
            )
            for finding in findings
            if finding not in eligible
        ]

        def progress(event: dict[str, Any]) -> None:
            if event.get("type") == "delta":
                preview = str(event.get("content", ""))
                chars = int(event.get("chars", 0))
                board.update(key, status="stream", preview=preview, chars=chars)
            elif event.get("type") == "usage":
                usage = event.get("usage") or {}
                board.update(key, tokens=int(usage.get("total_tokens") or 0))

        with semaphores[model_id]:
            if eligible:
                prompt_task = dict(task)
                prompt_task["prompt"] = build_voter_prompt(task, eligible)
                payload = call_model_with_retry(
                    model,
                    secrets,
                    prompt_task["prompt"],
                    timeout,
                    retry,
                    stream=stream,
                    stream_total_timeout=stream_total_timeout,
                    progress=progress,
                )
                vote = normalize_vote_payload(payload, model, task)
            else:
                vote = normalize_vote_payload({"votes": []}, model, task)
            existing_ids = {item.get("finding_id") for item in vote.get("votes", [])}
            vote["votes"].extend([item for item in skip_votes if item.get("finding_id") not in existing_ids])
            out = vote_path(votes_dir, model_id, task_id)
            out.parent.mkdir(parents=True, exist_ok=True)
            write_json_atomic(out, vote)
            board.update(key, status="done", done=True)
            return model_id, task_id

    print_info(
        "vote 任务："
        f"待运行 {len(jobs)}，已跳过 {skipped}，stream={stream}，"
        f"per_model_concurrency={per_model_concurrency}"
    )
    max_workers = max(1, sum(per_model_concurrency.values()))
    completed = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_one, model, task): (model, task) for model, task in jobs}
        try:
            for future in as_completed(futures):
                model, task = futures[future]
                try:
                    future.result()
                    completed += 1
                except Exception as exc:
                    failed += 1
                    board.update(f"{model.get('id')}/{task.get('task_id')}", status="failed", done=True)
                    print_warning(f"{model.get('id')}/{task.get('task_id')} 投票失败：{exc}")
        except KeyboardInterrupt:
            print_warning("收到 Ctrl+C：取消尚未开始/未写入的 vote 任务，等待正在写入的文件完成。")
            executor.shutdown(wait=True, cancel_futures=True)
            raise AiReviewError("vote 已中断，可重新运行命令恢复；hash 一致的已完成 vote 会跳过。")
    print_info(f"vote 完成：成功 {completed}，失败 {failed}，跳过 {skipped}")
    return 0


def command_merge_tasks(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    tasks_dir, votes_dir = task_dirs(review_dir)
    tasks = [normalize_task_payload(load_json(p, {})) for p in sorted(tasks_dir.glob("*.json"))]
    if args.limit:
        tasks = tasks[: int(args.limit)]
    model_map = configured_model_map(config)
    aggregates: dict[str, FindingAggregate] = {}
    task_by_finding: dict[str, dict[str, Any]] = {}
    for task in tasks:
        findings = load_host_findings(votes_dir, task)
        if not findings:
            print_warning(f"{task['task_id']} 没有有效 host-current findings，跳过 merge。")
            continue
        for finding in findings:
            aggregate = aggregate_finding(finding, task, votes_dir, model_map, config)
            aggregates[finding.finding_id] = aggregate
            task_by_finding[finding.finding_id] = task
            if aggregate.status == "PendingVote":
                print_warning(
                    f"{finding.finding_id} 缺失/失败投票比例 {aggregate.missing_vote_ratio:.2f} "
                    f"超过阈值，进入 PendingVote。"
                )
    print_info("merge 结果：")
    for finding_id, aggregate in aggregates.items():
        print(
            f"- {finding_id}: {aggregate.status} · {aggregate.finding.severity} · "
            f"{aggregate.finding.title} · score={aggregate.score:.2f} · votes={len(aggregate.all_votes)}"
        )
    if args.dry_run or not args.apply:
        return 0

    warnings = git_preflight(root, config, True)
    for warning in warnings:
        print_warning(warning)
    validate_issue_notes(review_dir)
    validate_task_sources(root, review_dir, tasks)

    units_by_id = {task["task_id"]: task_to_unit(root, task) for task in tasks}
    active_units_by_id = {
        task["task_id"]: units_by_id[task["task_id"]]
        for task in task_by_finding.values()
        if task["task_id"] in units_by_id
    }
    active_units = list(active_units_by_id.values())
    issue_ledger_path = review_dir / ".state" / "issue-ledger.json"
    unit_ledger_path = review_dir / ".state" / "review-unit-ledger.json"
    issue_ledger = load_json(issue_ledger_path, {"version": 1, "next_issue_id_hex": "0001", "issues": {}})
    unit_ledger = load_json(unit_ledger_path, {"version": 1, "next_unit_id": 1, "units": {}})
    existing_issues = collect_issues(review_dir)
    link_index = build_link_index(active_units)
    issue_links: dict[str, list[tuple[str, Path]]] = {}
    planned_issue_text: dict[Path, str] = {}
    planned_moves: list[tuple[Path, Path, str, str]] = []

    save_run_state(review_dir, {"version": 1, "active_run": {"stage": "MERGE_WRITING", "units": len(active_units)}, "last_runs": []})
    for finding_id, aggregate in aggregates.items():
        task = task_by_finding[finding_id]
        unit = units_by_id[task["task_id"]]
        open_existing = [
            item for item in existing_issues
            if item.get("source_unit_id") == unit.unit_id
            and item.get("source_finding_id") == aggregate.finding.finding_id
            and item.get("status") in {"Open", "PendingVote", "Rejected"}
        ]
        for item in open_existing:
            planned_moves.append((item["path"], issue_move_target(review_dir, item["path"], "Superseded"), "Superseded", item["id"]))
        issue_id = next_issue_id(issue_ledger)
        path = issue_path(review_dir, issue_id, aggregate.status, aggregate.finding.severity, aggregate.finding.title)
        issue_links.setdefault(unit.unit_id, []).append((issue_id, path.relative_to(root)))
        planned_issue_text[path] = render_issue(unit, issue_id, aggregate, path, root)
        issue_ledger.setdefault("issues", {})[issue_id] = {
            "status": aggregate.status.lower(),
            "severity": aggregate.finding.severity,
            "source_file": unit.rel_path,
            "source_unit_id": unit.unit_id,
            "source_finding_id": aggregate.finding.finding_id,
            "content_hash": unit.content_hash,
            "path": path.relative_to(root).as_posix(),
            "created_at": now_date(),
        }

    for src, dst, status, issue_id in planned_moves:
        text = update_issue_status_text(load_text(src), status)
        write_text_atomic(dst, text)
        if src != dst and src.exists():
            src.unlink()
        if issue_id in issue_ledger.get("issues", {}):
            issue_ledger["issues"][issue_id]["status"] = status.lower()
            issue_ledger["issues"][issue_id]["path"] = dst.relative_to(root).as_posix()
            issue_ledger["issues"][issue_id]["updated_at"] = now_date()
    for path, text in planned_issue_text.items():
        validate_frontmatter_text(text)
        write_text_atomic(path, text)
    by_file: dict[Path, list[ReviewUnit]] = {}
    for unit in active_units:
        by_file.setdefault(unit.file_path, []).append(unit)
    for path, units in by_file.items():
        updated = replace_ai_blocks_for_file(path, units, {}, issue_links)
        write_text_atomic(path, updated)
    write_json_atomic(unit_ledger_path, unit_ledger)
    write_json_atomic(issue_ledger_path, issue_ledger)
    write_json_atomic(review_dir / ".state" / "link-index.json", link_index)
    write_text_atomic(review_dir / "Dashboard.md", render_dashboard(review_dir, int(deep_get(config, "dashboard.top_n_per_section", 10))))
    for warning in validate_markdown_and_links(root, list(planned_issue_text) + list(by_file)):
        print_warning(warning)
    diff = run_git(["diff", "--stat"], root)
    print(diff.stdout.rstrip())
    save_run_state(review_dir, {"version": 1, "active_run": None, "last_runs": [{"mode": "merge-apply", "finished_at": _dt.datetime.now().isoformat(), "units": len(active_units)}]})
    print_info("merge 写入完成。")
    return 0


def command_identity(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    ensure_review_dirs(root, review_dir)
    warnings = git_preflight(root, config, bool(args.apply))
    for warning in warnings:
        print_warning(warning)

    unit_ledger_path = review_dir / ".state" / "review-unit-ledger.json"
    unit_ledger = load_json(unit_ledger_path, {"version": 1, "next_unit_id": 1, "units": {}})
    files, units = discover_units_for_args(root, config, review_dir, args, unit_ledger)
    skipped_submodules = dirty_submodule_paths(root, config, bool(args.apply))
    if skipped_submodules:
        kept_files = []
        for path in files:
            if any(is_under_repo_rel(path, root, rel) for rel in skipped_submodules):
                continue
            kept_files.append(path)
        files = kept_files
        units = [
            unit for unit in units
            if not any(is_under_repo_rel(unit.file_path, root, rel) for rel in skipped_submodules)
        ]
        for rel in sorted(skipped_submodules):
            print_warning(f"identity 跳过 dirty/unavailable submodule：{rel}")
    by_file: dict[Path, list[ReviewUnit]] = {}
    for unit in units:
        by_file.setdefault(unit.file_path, []).append(unit)

    planned: list[tuple[Path, str, int, int]] = []
    total_created = 0
    for path, file_units in by_file.items():
        updated, created = replace_identity_blocks_for_file(path, file_units)
        total_created += created
        planned.append((path, updated, created, len(file_units)))

    print_info(f"identity 扫描 Markdown 文件 {len(files)} 个，非空 ReviewUnit {len(units)} 个。")
    duplicates = duplicate_existing_blocks(files, root)
    for unit_id, locations in sorted(duplicates.items()):
        shown = ", ".join(locations[:5])
        suffix = " ..." if len(locations) > 5 else ""
        print_warning(f"发现重复 identity ID {unit_id}：{shown}{suffix}")
    for path, _updated, created, count in planned:
        rel = path.relative_to(root).as_posix()
        print(f"- {rel}: units={count}, new_identity_blocks={created}")

    if args.dry_run or not args.apply:
        print_info("identity dry-run：未写入源文。使用 --apply 写入缺失的 AI-Review identity 块。")
        return 0

    for path, updated, _created, _count in planned:
        write_text_atomic(path, updated)
    write_json_atomic(unit_ledger_path, unit_ledger)
    print_info(f"identity 写入完成：新增 identity 块 {total_created} 个。")
    return 0


def discover_units_for_args(
    root: Path,
    config: dict[str, Any],
    review_dir: Path,
    args: argparse.Namespace,
    unit_ledger: dict[str, Any],
) -> tuple[list[Path], list[ReviewUnit]]:
    scope = "all" if getattr(args, "all", False) else "changed"
    files = list_markdown_files(root, review_dir, scope, getattr(args, "paths", []))
    all_units: list[ReviewUnit] = []
    claimed_ids: dict[str, str] = {}
    for path in files:
        all_units.extend(split_units(path, root, unit_ledger, claimed_ids))
    issue_id = getattr(args, "issue", None)
    if issue_id:
        issue = next((x for x in collect_issues(review_dir) if x["id"] == issue_id), None)
        if not issue:
            raise AiReviewError(f"未找到 issue：{issue_id}")
        all_units = [
            u for u in all_units
            if u.unit_id == issue["source_unit_id"] or u.rel_path.strip('"') == issue["source_file"].strip('"')
        ]
    limit = getattr(args, "limit", None)
    if limit:
        all_units = all_units[: int(limit)]
    return files, all_units


def serialize_unit_for_task(root: Path, unit: ReviewUnit, config: dict[str, Any], warning_keys: set[str]) -> dict[str, Any]:
    context_notes = build_context_notes(root, unit, config, warning_keys)
    return {
        "version": 1,
        "schema_version": 1,
        "kind": "ai-review-task",
        "task_id": unit.unit_id,
        "unit_id": unit.unit_id,
        "task_hash": unit.content_hash,
        "content_hash": unit.content_hash,
        "source_file": unit.rel_path,
        "source_block_ref": source_block_ref(unit),
        "heading_path": unit.heading_path,
        "heading": unit.heading,
        "level": unit.level,
        "start_line": unit.start_line,
        "end_line": unit.end_line,
        "content_hash": unit.content_hash,
        "requires_multimodal": unit.requires_multimodal,
        "attachments": unit.attachments,
        "outlinks": unit.outlinks,
        "tags": unit.tags,
        "context_notes": context_notes,
        "prepared_context": context_notes,
        "external_sources": [],
        "content": unit.content,
        "prompt": build_prompt(unit, context_notes),
    }


def units_missing_identity(root: Path, units: list[ReviewUnit]) -> list[ReviewUnit]:
    blocks_by_file: dict[Path, dict[str, str]] = {}
    missing: list[ReviewUnit] = []
    for unit in units:
        blocks = blocks_by_file.get(unit.file_path)
        if blocks is None:
            blocks = existing_ai_blocks_by_unit(load_text(unit.file_path))
            blocks_by_file[unit.file_path] = blocks
        if unit.unit_id not in blocks:
            missing.append(unit)
    return missing


def command_prepare_tasks(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    ensure_review_dirs(root, review_dir)
    warning_keys: set[str] = set()
    warnings = git_preflight(root, config, bool(getattr(args, "apply", False)))
    for warning in warnings:
        print_warning(warning)
    validate_issue_notes(review_dir)
    unit_ledger = load_json(review_dir / ".state" / "review-unit-ledger.json", {"version": 1, "next_unit_id": 1, "units": {}})
    files, units = discover_units_for_args(root, config, review_dir, args, unit_ledger)
    if getattr(args, "unit", None):
        units = [unit for unit in units if unit.unit_id == args.unit]
        if not units:
            raise AiReviewError(f"未找到 ReviewUnit：{args.unit}")

    missing = units_missing_identity(root, units)
    if missing:
        examples = ", ".join(f"{unit.rel_path}:{unit.start_line}({unit.unit_id})" for unit in missing[:5])
        raise AiReviewError(f"prepare 前必须先写入 identity；缺失示例：{examples}。请先运行 identity --apply。")

    tasks_dir, _votes_dir = task_dirs(review_dir)
    planned_tasks = [serialize_unit_for_task(root, unit, config, warning_keys) for unit in units]
    written = 0
    skipped = 0
    for task in planned_tasks:
        out = task_path(tasks_dir, task["task_id"])
        old = load_json(out, None) if out.exists() else None
        if old and old.get("task_hash") == task.get("task_hash") and not getattr(args, "regenerate", False):
            skipped += 1
            continue
        if getattr(args, "apply", False):
            write_json_atomic(out, task)
            written += 1

    index = {
        "version": 1,
        "schema_version": 1,
        "kind": "ai-review-tasks-index",
        "updated_at": _dt.datetime.now().isoformat(),
        "scope": "all" if getattr(args, "all", False) else "changed",
        "files": [p.relative_to(root).as_posix() for p in files],
        "tasks": [
            {
                "task_id": task["task_id"],
                "task_hash": task["task_hash"],
                "source_file": task["source_file"],
                "source_block_ref": task["source_block_ref"],
                "heading_path": task["heading_path"],
            }
            for task in planned_tasks
        ],
        "warnings": sorted(warning_keys),
    }
    if getattr(args, "apply", False):
        write_json_atomic(review_dir / ".state" / "tasks-index.json", index)

    print_info(f"prepare 扫描 Markdown 文件 {len(files)} 个，候选 task {len(planned_tasks)} 个。")
    print_info(f"prepare 结果：写入 {written}，跳过 {skipped}，dry_run={not getattr(args, 'apply', False)}")
    for task in planned_tasks:
        print(f"- {task['task_id']}: {task['source_file']}:{task['start_line']}-{task['end_line']} · context={len(task['context_notes'])} · sources={len(task['external_sources'])}")
    if getattr(args, "print_json", False):
        print(json.dumps({"tasks": planned_tasks, "index": index}, ensure_ascii=False, indent=2))
    return 0


def validate_frontmatter_text(text: str) -> None:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise AiReviewError("frontmatter 校验失败。")
    if text.count("<!-- user-notes:start -->") != 1 or text.count("<!-- user-notes:end -->") != 1:
        raise AiReviewError("人工备注区校验失败。")


def validate_maintenance_contract(root: Path) -> list[str]:
    warnings: list[str] = []
    for relative_path in MAINTENANCE_CONTRACT_FILES:
        if not (root / relative_path).exists():
            warnings.append(f"维护同步文件缺失：{relative_path}")
    return warnings


def command_dashboard(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    ensure_review_dirs(root, review_dir)
    output = render_dashboard(review_dir, int(deep_get(config, "dashboard.top_n_per_section", 10)))
    if args.dry_run:
        print(output)
    else:
        write_text_atomic(review_dir / "Dashboard.md", output)
        print_info("Dashboard 已更新。")
    return 0


def command_check(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    ensure_review_dirs(root, review_dir)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        validate_issue_notes(review_dir)
    except AiReviewError as exc:
        errors.append(str(exc))
    warnings.extend(validate_maintenance_contract(root))
    warnings.extend(git_preflight(root, config, False))
    warnings.extend(validate_markdown_and_links(root, list(review_dir.rglob("*.md"))))
    for warning in warnings:
        print_warning(warning)
    if errors:
        for error in errors:
            print(f"[ai-review][error] {error}", file=sys.stderr)
        return 1
    print_info("check 通过。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-review", description="AI Review CLI")
    sub = parser.add_subparsers(dest="command")

    identity = sub.add_parser("identity", help="为非空 ReviewUnit 写入稳定 AI-Review identity 块")
    identity_scope = identity.add_mutually_exclusive_group()
    identity_scope.add_argument("--changed", action="store_true", help="只处理 Git 变更文件")
    identity_scope.add_argument("--all", action="store_true", help="处理全仓库")
    identity.add_argument("paths", nargs="*", help="指定文件或目录")
    identity.add_argument("--issue", help="只定位指定 issue 对应段落")
    identity.add_argument("--limit", type=int, help="最多处理 N 个 ReviewUnit")
    identity_mode = identity.add_mutually_exclusive_group()
    identity_mode.add_argument("--dry-run", action="store_true", help="只预览，不写入源文")
    identity_mode.add_argument("--apply", action="store_true", help="写入缺失的 AI-Review identity 块")

    prepare = sub.add_parser("prepare", help="生成 .state/tasks/{task}.json task 队列")
    prepare_scope = prepare.add_mutually_exclusive_group()
    prepare_scope.add_argument("--changed", action="store_true", help="只准备 Git 变更文件")
    prepare_scope.add_argument("--all", action="store_true", help="准备全仓库")
    prepare.add_argument("paths", nargs="*", help="指定文件或目录")
    prepare.add_argument("--issue", help="准备复查指定 issue")
    prepare.add_argument("--unit", help="只准备指定 ReviewUnit id")
    prepare.add_argument("--limit", type=int, help="最多准备 N 个 task")
    prepare_mode = prepare.add_mutually_exclusive_group()
    prepare_mode.add_argument("--dry-run", action="store_true", help="只预览，不写入 task 文件")
    prepare_mode.add_argument("--apply", action="store_true", help="写入 task 文件和 tasks-index.json")
    prepare.add_argument("--regenerate", action="store_true", help="覆盖 task_hash 一致的既有 task")
    prepare.add_argument("--print-json", action="store_true", help="同时向 stdout 打印 task JSON")

    vote = sub.add_parser("vote", help="并行调用外部 reviewer，写入 .state/votes/{model}/{task}.json")
    vote.add_argument("--model", help="只运行指定模型 id；默认运行所有启用 voter")
    vote.add_argument("--limit", type=int, help="最多处理 N 个 task")
    vote.add_argument("--concurrency", type=int, help="临时覆盖每个模型的并发数")
    vote.add_argument("--model-timeout", type=int, help="socket 空闲超时秒数；流式输出持续到达时不会触发")
    vote.add_argument("--model-retry", type=int, help="临时覆盖外部模型重试次数")
    vote.add_argument("--stream-total-timeout", type=int, help="单个流式 review 的总时长上限秒数")

    task_merge = sub.add_parser("merge", help="聚合 .state/votes 中所有成功投票并更新结果")
    task_merge_mode = task_merge.add_mutually_exclusive_group()
    task_merge_mode.add_argument("--dry-run", action="store_true", help="只预览聚合结果")
    task_merge_mode.add_argument("--apply", action="store_true", help="写入 issue、源文件 AI 块和 Dashboard")
    task_merge.add_argument("--limit", type=int, help="最多聚合 N 个 task")

    dashboard = sub.add_parser("dashboard", help="更新 Dashboard")
    dashboard.add_argument("--dry-run", action="store_true")
    sub.add_parser("check", help="检查配置、状态和链接")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        args = parser.parse_args(["check"])
    try:
        if args.command == "identity":
            if not args.dry_run and not args.apply:
                args.dry_run = True
            if not args.changed and not args.all and not args.paths:
                default = load_yaml(Path.cwd() / ".ai-review.yaml").get("default_mode", {})
                args.changed = str(default.get("scope", "changed")) == "changed"
            return command_identity(args)
        if args.command == "prepare":
            if not args.dry_run and not args.apply:
                default = load_yaml(Path.cwd() / ".ai-review.yaml").get("default_mode", {})
                args.dry_run = bool(default.get("dry_run", True))
            if not args.changed and not args.all and not args.paths and not args.issue and not args.unit:
                default = load_yaml(Path.cwd() / ".ai-review.yaml").get("default_mode", {})
                args.changed = str(default.get("scope", "changed")) == "changed"
            return command_prepare_tasks(args)
        if args.command == "vote":
            return command_vote_tasks(args)
        if args.command == "merge":
            if not args.dry_run and not args.apply:
                default = load_yaml(Path.cwd() / ".ai-review.yaml").get("default_mode", {})
                args.dry_run = bool(default.get("dry_run", True))
            return command_merge_tasks(args)
        if args.command == "dashboard":
            return command_dashboard(args)
        if args.command == "check":
            return command_check(args)
        parser.error(f"未知命令：{args.command}")
        return 2
    except KeyboardInterrupt:
        print_warning("运行被中断。")
        return 130
    except AiReviewError as exc:
        print(f"[ai-review][error] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
