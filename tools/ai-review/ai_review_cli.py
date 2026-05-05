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
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

from ai_review_lib.model_client import (
    ModelClientError,
    call_model,
    call_model_with_retry,
    endpoint_for_provider,
)
from ai_review_lib.path_filter import configured_excludes, is_path_excluded


SEVERITY_ORDER = ["Correct", "Enhance", "Minor", "Major", "Critical", "Unknown"]
ISSUE_SEVERITIES = {"Enhance", "Minor", "Major", "Critical", "Unknown"}
STATUS_DIRS = {"open": "Open", "closed": "Closed", "superseded": "Superseded", "unknown": "Unknown"}
AI_BLOCK_RE = re.compile(
    r"(?ms)^<!-- ai-review:start unit=ru[0-9]{6} -->.*?^<!-- ai-review:end -->\s*"
)
SUSPICIOUS_ENCODING_RE = re.compile(r"\?{4,}|\ufffd")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
WIKI_LINK_RE = re.compile(r"!?\[\[([^\]]+)\]\]")
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")
TAG_RE = re.compile(r"(?<!\w)#([\w\-\u4e00-\u9fff/]+)")
USER_NOTES_RE = re.compile(
    r"(?ms)<!-- user-notes:start -->.*?<!-- user-notes:end -->"
)


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
    for raw in lines:
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
                item: dict[str, Any] = {key.strip(): parse_scalar(val)}
                parent.append(item)
                stack.append((indent, item))
            else:
                parent.append(parse_scalar(item_text))
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val == "":
            next_container: Any = {}
            parent[key] = next_container
            stack.append((indent, next_container))
        else:
            parent[key] = parse_scalar(val)
        next_index = lines.index(raw) + 1
        if val == "" and next_index < len(lines):
            pass
    # Convert empty dicts that are followed by list syntax is intentionally not
    # attempted here. Current repository config is parsed by PyYAML in normal use.
    return root


def deep_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
    cur: Any = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def ensure_review_dirs(root: Path, review_dir: Path) -> None:
    for rel in ["Open", "Closed", "Superseded", "Unknown", ".state", ".tmp", ".cache"]:
        (review_dir / rel).mkdir(parents=True, exist_ok=True)
    for rel in ["Open/.gitkeep", "Closed/.gitkeep", "Superseded/.gitkeep", "Unknown/.gitkeep"]:
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


@dataclasses.dataclass
class Vote:
    unit_id: str
    model_id: str
    model_role: str
    result: str
    severity: str
    confidence: float
    title: str
    topic: list[str]
    summary: str
    evidence: list[str]
    suggested_fix: str
    requires_multimodal: bool
    context_used: list[str]
    relation_to_previous_issue: str
    external_sources: list[str]
    weight: float
    display_name: str

    @classmethod
    def from_json(cls, payload: dict[str, Any], model: dict[str, Any], unit_id: str) -> "Vote":
        severity = str(payload.get("severity") or "Unknown")
        if severity not in SEVERITY_ORDER:
            severity = "Unknown"
        result = str(payload.get("result") or ("correct" if severity == "Correct" else "issue")).lower()
        if result not in {"correct", "issue", "unknown"}:
            result = "unknown"
        confidence = payload.get("confidence", 0.0)
        try:
            confidence = max(0.0, min(1.0, float(confidence)))
        except Exception:
            confidence = 0.0
        topic = payload.get("topic") or []
        if isinstance(topic, str):
            topic = [topic]
        evidence = payload.get("evidence") or []
        if isinstance(evidence, str):
            evidence = [evidence]
        context_used = payload.get("context_used") or ["current_unit"]
        if isinstance(context_used, str):
            context_used = [context_used]
        external_sources = payload.get("external_sources") or []
        if isinstance(external_sources, str):
            external_sources = [external_sources]
        return cls(
            unit_id=str(payload.get("unit_id") or unit_id),
            model_id=str(payload.get("model_id") or model.get("id") or "unknown-model"),
            model_role=str(payload.get("model_role") or model.get("role") or "voter"),
            result=result,
            severity=severity,
            confidence=confidence,
            title=str(payload.get("title") or ""),
            topic=[str(x) for x in topic][:8],
            summary=str(payload.get("summary") or ""),
            evidence=[str(x) for x in evidence][:8],
            suggested_fix=str(payload.get("suggested_fix") or ""),
            requires_multimodal=bool(payload.get("requires_multimodal", False)),
            context_used=[str(x) for x in context_used],
            relation_to_previous_issue=str(payload.get("relation_to_previous_issue") or "not_applicable"),
            external_sources=[str(x) for x in external_sources][:12],
            weight=float(model.get("weight", 1)),
            display_name=str(model.get("display_name") or model.get("id") or payload.get("model_id") or "unknown-model"),
        )


@dataclasses.dataclass
class AggregateResult:
    severity: str
    result: str
    score_by_severity: dict[str, float]
    normalized_score_by_severity: dict[str, float]
    votes: list[Vote]
    title: str
    topic: list[str]
    summary: str
    evidence: list[str]
    suggested_fix: str
    requires_multimodal: bool
    external_sources: list[str]


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


def split_units(path: Path, root: Path, unit_ledger: dict[str, Any]) -> list[ReviewUnit]:
    original = load_text(path)
    text = AI_BLOCK_RE.sub("", original)
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
    for start, end, level, heading, heading_path in ranges:
        content = "\n".join(lines[start:end]).rstrip() + "\n"
        normalized = normalize_unit_text(content)
        content_hash = sha256_text(normalized)
        locator = f"{rel_path}::{' > '.join(heading_path)}"
        existing = detect_existing_unit_id(original)
        unit_id = by_locator.get(locator, {}).get("unit_id") or by_hash.get(content_hash)
        if not unit_id and existing and len(ranges) == 1:
            unit_id = existing
        if not unit_id:
            next_id = int(unit_ledger.get("next_unit_id", 1))
            unit_id = f"ru{next_id:06d}"
            unit_ledger["next_unit_id"] = next_id + 1
        by_locator[locator] = {
            "unit_id": unit_id,
            "file": rel_path,
            "heading_path": heading_path,
            "content_hash": content_hash,
            "updated_at": now_date(),
        }
        by_hash[content_hash] = unit_id
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
        你是 AI Review 投票模型。请只返回符合协议的 JSON，不要输出 Markdown。

        审查目标：
        - unit_id: {unit.unit_id}
        - source_file: {unit.rel_path}
        - heading_path: {heading}
        - content_hash: {unit.content_hash}

        要求：
        - 自然语言字段必须以简体中文为主。
        - 只审查当前 ReviewUnit，不要直接改写原文。
        - severity 只能是 Correct/Enhance/Minor/Major/Critical/Unknown。
        - topic 只用于 issue 和 Dashboard。
        - 如果依赖图片且无法判断，返回 Unknown。
        - 如果当前知识不足、事实可能过时，或需要核验权威资料，host-current 主模型必须联网查询。
        - 联网查询时必须在 JSON 中增加 external_sources，列出 URL 或可追溯来源；summary/evidence 应明确哪些判断来自外部资料。

        附加上下文：
        {json.dumps(context_notes, ensure_ascii=False)}

        ReviewUnit 原文：
        ```markdown
        {unit.content}
        ```
        """
    ).strip()


def load_host_votes(path: str | None) -> dict[str, dict[str, Any]]:
    raw = os.environ.get("AI_REVIEW_HOST_CURRENT_VOTES_JSON", "")
    if path:
        vote_path = Path(path)
        if not vote_path.exists():
            raise AiReviewError(f"host-current 投票文件不存在：{path}")
        raw = load_text(vote_path)
    if not raw:
        return {}
    data = json.loads(raw)
    if isinstance(data, list):
        return {str(item.get("unit_id")): item for item in data if isinstance(item, dict)}
    if isinstance(data, dict) and "unit_id" in data:
        return {str(data.get("unit_id")): data}
    if isinstance(data, dict):
        return {str(k): v for k, v in data.items() if isinstance(v, dict)}
    raise AiReviewError("host-current 投票 JSON 必须是对象、数组或 unit_id 映射。")


def collect_votes(
    unit: ReviewUnit,
    config: dict[str, Any],
    secrets: dict[str, Any],
    args: argparse.Namespace,
    context_notes: list[str],
    host_votes: dict[str, dict[str, Any]],
    warning_keys: set[str],
) -> list[Vote]:
    votes: list[Vote] = []
    if getattr(args, "no_external", False):
        payload = host_votes.get(unit.unit_id)
        main = dict(deep_get(config, "models.main", {}) or {})
        if payload:
            return [Vote.from_json(payload, {**main, "role": "main"}, unit.unit_id)]
        return []
    main = dict(deep_get(config, "models.main", {}) or {})
    main_mode = args.main or main.get("mode") or "host-current"
    if main_mode == "host-current" and main.get("vote_enabled", True):
        payload = host_votes.get(unit.unit_id)
        if payload:
            votes.append(Vote.from_json(payload, {**main, "role": "main"}, unit.unit_id))
        else:
            key = "host-current-missing"
            if key not in warning_keys:
                warning_keys.add(key)
                print_warning("host-current 主模型投票未注入；独立 CLI 无法直接读取当前 Codex/Cursor 模型。")
    elif main_mode == "configured":
        model = dict(deep_get(config, "models.configured_main", {}) or {})
        model.setdefault("role", "main")
        if model.get("vote_enabled", True):
            try:
                payload = call_model(
                    model,
                    secrets,
                    build_prompt(unit, context_notes),
                    int(deep_get(config, "runtime.request_timeout_sec", 120)),
                    stream=bool(deep_get(config, "runtime.stream", False)),
                    stream_total_timeout=int(deep_get(config, "runtime.stream_total_timeout_sec", 240)),
                )
                votes.append(Vote.from_json(payload, model, unit.unit_id))
            except Exception as exc:
                warn_once(warning_keys, f"main:{model.get('id')}", f"主模型 `{model.get('id')}` 调用失败：{exc}")
    elif main_mode == "none":
        pass
    else:
        raise AiReviewError(f"不支持的主模型模式：{main_mode}")

    voter_jobs: list[dict[str, Any]] = []
    for model in deep_get(config, "models.voters", []) or []:
        if not model.get("vote_enabled", True):
            continue
        if unit.requires_multimodal and not model.get("multimodal", False):
            warn_once(warning_keys, f"multimodal:{model.get('id')}", f"模型 `{model.get('id')}` 不支持多模态，跳过依赖图片的 ReviewUnit。")
            continue
        voter_jobs.append(model)
    timeout = int(deep_get(config, "runtime.request_timeout_sec", 120))
    if getattr(args, "model_timeout", None):
        timeout = int(args.model_timeout)
    max_workers = max(1, int(deep_get(config, "runtime.max_concurrency", 3)))
    retry = max(0, int(deep_get(config, "runtime.retry", 0)))
    if getattr(args, "model_retry", None) is not None:
        retry = max(0, int(args.model_retry))
    prompt = build_prompt(unit, context_notes)
    stream = bool(deep_get(config, "runtime.stream", False))
    stream_total_timeout = int(deep_get(config, "runtime.stream_total_timeout_sec", 240))
    if getattr(args, "stream_total_timeout", None):
        stream_total_timeout = int(args.stream_total_timeout)
    for model in voter_jobs:
        print_info(f"{unit.unit_id} 调用外部 voter `{model.get('id')}`，timeout={timeout}s，retry={retry}，stream={stream}，stream_total_timeout={stream_total_timeout}s")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(call_model_with_retry, model, secrets, prompt, timeout, retry, stream=stream, stream_total_timeout=stream_total_timeout): model
            for model in voter_jobs
        }
        for future in as_completed(futures):
            model = futures[future]
            try:
                payload = future.result()
                votes.append(Vote.from_json(payload, model, unit.unit_id))
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, AiReviewError, ModelClientError) as exc:
                warn_once(warning_keys, f"voter:{model.get('id')}:{type(exc).__name__}", f"voter `{model.get('id')}` 调用失败：{exc}")
            except Exception as exc:
                warn_once(warning_keys, f"voter:{model.get('id')}:unknown", f"voter `{model.get('id')}` 调用异常：{exc}")
    return votes


def warn_once(keys: set[str], key: str, message: str) -> None:
    if key not in keys:
        keys.add(key)
        print_warning(message)


def aggregate_votes(votes: list[Vote], config: dict[str, Any]) -> AggregateResult:
    # 中文说明：主模型和 voter 在这里完全等价，统一按
    # `模型权重 × 置信度` 累加，避免 host-current 在聚合阶段隐式覆盖。
    total_weight = sum(v.weight for v in votes) or 1.0
    scores = {sev: 0.0 for sev in SEVERITY_ORDER}
    for vote in votes:
        scores[vote.severity] = scores.get(vote.severity, 0.0) + vote.weight * vote.confidence
    normalized = {sev: score / total_weight for sev, score in scores.items()}
    thresholds = deep_get(config, "voting.severity_thresholds", {}) or {}
    candidates = []
    for sev in SEVERITY_ORDER:
        threshold = float(deep_get({"x": thresholds}, f"x.{sev}.min_normalized_score", 0.0))
        if normalized.get(sev, 0.0) >= threshold:
            candidates.append((scores.get(sev, 0.0), SEVERITY_ORDER.index(sev), sev))
    if candidates:
        candidates.sort(reverse=True)
        severity = candidates[0][2]
    else:
        severity = str(deep_get(config, "voting.fallback_when_no_threshold_matched", "Unknown"))
    if severity not in SEVERITY_ORDER:
        severity = "Unknown"
    result = "correct" if severity == "Correct" else ("unknown" if severity == "Unknown" else "issue")
    issue_votes = [v for v in votes if v.severity == severity] or votes
    title = next((v.title for v in issue_votes if v.title), "")
    summary = next((v.summary for v in issue_votes if v.summary), "未发现可用模型投票；按配置标记为 Unknown。")
    suggested_fix = next((v.suggested_fix for v in issue_votes if v.suggested_fix), "")
    topic: list[str] = []
    evidence: list[str] = []
    external_sources: list[str] = []
    for vote in issue_votes:
        for item in vote.topic:
            if item and item not in topic:
                topic.append(item)
        for item in vote.evidence:
            if item and item not in evidence:
                evidence.append(item)
        for item in vote.external_sources:
            if item and item not in external_sources:
                external_sources.append(item)
    return AggregateResult(
        severity=severity,
        result=result,
        score_by_severity=scores,
        normalized_score_by_severity=normalized,
        votes=votes,
        title=title or ("无法判断" if severity == "Unknown" else "未命名问题"),
        topic=topic[:8] or ["未分类"],
        summary=summary,
        evidence=evidence[:8],
        suggested_fix=suggested_fix,
        requires_multimodal=any(v.requires_multimodal for v in votes),
        external_sources=external_sources[:12],
    )


def fallback_unknown_vote(unit: ReviewUnit, reason: str) -> Vote:
    return Vote(
        unit_id=unit.unit_id,
        model_id="ai-review-cli",
        model_role="voter",
        result="unknown",
        severity="Unknown",
        confidence=0.8,
        title="没有可用模型完成审查",
        topic=["模型不可用"],
        summary=reason,
        evidence=[],
        suggested_fix="请配置可用模型或从支持 host-current 的宿主入口重新运行。",
        requires_multimodal=unit.requires_multimodal,
        context_used=["current_unit"],
        relation_to_previous_issue="not_applicable",
        external_sources=[],
        weight=1.0,
        display_name="AI Review CLI",
    )


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


def issue_path(review_dir: Path, issue_id: str, severity: str, title: str) -> Path:
    status_dir = "Unknown" if severity == "Unknown" else "Open"
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


def render_issue(unit: ReviewUnit, issue_id: str, aggregate: AggregateResult, issue_file: Path, root: Path) -> str:
    today = now_date()
    head = git_head(root)
    status = "unknown" if aggregate.severity == "Unknown" else "open"
    topic_yaml = yaml_list(aggregate.topic, 2)
    heading_yaml = yaml_list(unit.heading_path, 2)
    models_supported = [v.model_id for v in aggregate.votes]
    models_yaml = yaml_list(models_supported, 2)
    votes_rows = []
    for v in aggregate.votes:
        conclusion = {"correct": "正确", "issue": "有问题", "unknown": "无法判断"}.get(v.result, v.result)
        votes_rows.append(
            f"| {v.display_name} | {v.model_role} | {conclusion} | {v.severity} | {v.confidence:.2f} | {v.weight:g} | {v.confidence * v.weight:.2f} |"
        )
    evidence = "\n".join(f"- {x}" for x in aggregate.evidence) if aggregate.evidence else "暂无。"
    external_sources = "\n".join(f"- {x}" for x in aggregate.external_sources) if aggregate.external_sources else "暂无。"
    suggested = aggregate.suggested_fix or "暂无；AI Review 不直接修改原文正文。"
    return textwrap.dedent(
        f"""\
        ---
        id: {issue_id}
        status: {status}
        severity: {aggregate.severity}
        source_file: {json.dumps(unit.rel_path, ensure_ascii=False)}
        source_unit_id: {json.dumps(unit.unit_id, ensure_ascii=False)}
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
        {models_yaml}
        models_disagreed: []
        tags:
          - AI-Review
        ---

        # {aggregate.title} ^{issue_id}

        #AI-Review

        ## 原文位置

        - {source_block_ref(unit)}

        ## 问题等级

        {aggregate.severity}

        ## Topic

        {chr(10).join(f"- {x}" for x in aggregate.topic)}

        ## 问题摘要

        {aggregate.summary}

        ## 模型投票

        | 模型 | 角色 | 结论 | 等级 | 置信度 | 权重 | 加权得分 |
        |---|---|---|---|---:|---:|---:|
        {chr(10).join(votes_rows) if votes_rows else "| 无 | - | 无可用投票 | Unknown | 0.00 | 0 | 0.00 |"}

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


def render_ai_block(unit: ReviewUnit, aggregate: AggregateResult, issues: list[tuple[str, Path]], model_names: list[str]) -> str:
    callout = {
        "Correct": "success",
        "Enhance": "tip",
        "Minor": "attention",
        "Major": "bug",
        "Critical": "danger",
        "Unknown": "question",
    }.get(aggregate.severity, "question")
    lines = [f"<!-- ai-review:start unit={unit.unit_id} -->", f"> [!{callout}]- AI Review `{unit.unit_id}`"]
    if aggregate.severity == "Correct":
        lines.append("> - [[AI-Review/Dashboard|Dashboard]]")
    else:
        for issue_id, path in issues:
            link = path.with_suffix("").as_posix()
            lines.append(f"> - [ ] [[{link}|{issue_id}]]")
    names = "/".join(model_names) if model_names else "无可用模型"
    lines.append(f"> `{now_date()}` · {names}")
    lines.append(f"^{unit.unit_id}")
    lines.append("<!-- ai-review:end -->")
    return "\n".join(lines) + "\n"


def replace_ai_blocks_for_file(path: Path, units: list[ReviewUnit], aggregates: dict[str, AggregateResult], issue_links: dict[str, list[tuple[str, Path]]]) -> str:
    text = AI_BLOCK_RE.sub("", load_text(path)).rstrip() + "\n"
    lines = text.splitlines()
    inserts: dict[int, str] = {}
    for unit in units:
        aggregate = aggregates[unit.unit_id]
        model_names = [v.display_name for v in aggregate.votes]
        inserts[unit.end_line] = render_ai_block(unit, aggregate, issue_links.get(unit.unit_id, []), model_names)
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
    for status_dir in ["Open", "Closed", "Superseded", "Unknown"]:
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
                    "title": re.search(r"^# (.+?)(?: \^ar[0-9a-f]+)?$", text, re.M).group(1)
                    if re.search(r"^# (.+?)(?: \^ar[0-9a-f]+)?$", text, re.M)
                    else path.stem,
                    "topic": topics,
                }
            )
    return sorted(items, key=lambda x: x["id"])


def render_dashboard(review_dir: Path, top_n: int) -> str:
    issues = collect_issues(review_dir)
    counts = {status: 0 for status in ["Open", "Closed", "Superseded", "Unknown"]}
    for item in issues:
        counts[item["status"]] += 1
    open_like = [x for x in issues if x["status"] in {"Open", "Unknown"}]
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
    unknown_lines = []
    for item in [x for x in issues if x["status"] == "Unknown"][:top_n]:
        link = item["path"].with_suffix("").as_posix()
        unknown_lines.append(f"- [[{link}|{item['id']}]] · {item['title']}")
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
        | Superseded | {counts['Superseded']} |
        | Unknown | {counts['Unknown']} |

        ## 当前最重要问题 Top N

        {chr(10).join(top_lines) if top_lines else "暂无。"}

        ## 按 Topic 聚合

        {chr(10).join(topic_lines) if topic_lines else "暂无。"}

        ## 已勾选但复查失败

        暂无。

        ## Unknown / 需要人工确认

        {chr(10).join(unknown_lines) if unknown_lines else "暂无。"}
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
        allowed = []
        for line in proc.stdout.splitlines():
            if "AI-Review/.tmp/" in line or "AI-Review/.cache/" in line:
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


def normalize_vote_payload(payload: dict[str, Any], model: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    vote = dict(payload)
    vote["version"] = vote.get("version", 1)
    vote["task_id"] = vote.get("task_id") or vote.get("unit_id") or task["task_id"]
    vote["unit_id"] = vote["task_id"]
    vote["task_hash"] = vote.get("task_hash") or task["task_hash"]
    vote["content_hash"] = vote["task_hash"]
    vote["model_id"] = vote.get("model_id") or model.get("id")
    vote["model_role"] = vote.get("model_role") or "reviewer"
    vote["created_at"] = vote.get("created_at") or _dt.datetime.now().isoformat()
    return vote


def reviewer_models(config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    voters = [dict(x) for x in deep_get(config, "models.voters", []) or [] if x.get("vote_enabled", True)]
    if getattr(args, "model", None):
        voters = [x for x in voters if x.get("id") == args.model]
    return voters


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

        def progress(event: dict[str, Any]) -> None:
            if event.get("type") == "delta":
                preview = str(event.get("content", ""))
                chars = int(event.get("chars", 0))
                board.update(key, status="stream", preview=preview, chars=chars)
            elif event.get("type") == "usage":
                usage = event.get("usage") or {}
                board.update(key, tokens=int(usage.get("total_tokens") or 0))

        with semaphores[model_id]:
            payload = call_model_with_retry(
                model,
                secrets,
                str(task.get("prompt") or ""),
                timeout,
                retry,
                stream=stream,
                stream_total_timeout=stream_total_timeout,
                progress=progress,
            )
            vote = normalize_vote_payload(payload, model, task)
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
    model_map = {str(m.get("id")): dict(m) for m in deep_get(config, "models.voters", []) or []}
    main = dict(deep_get(config, "models.main", {}) or {})
    model_map[str(main.get("id", "host-current"))] = {**main, "role": "reviewer"}
    aggregates: dict[str, AggregateResult] = {}
    for task in tasks:
        votes: list[Vote] = []
        for path in votes_dir.glob(f"*/{task['task_id']}.json"):
            payload = load_json(path, {})
            if payload.get("task_hash") != task.get("task_hash"):
                continue
            model_id = str(payload.get("model_id") or path.parent.name)
            model = model_map.get(model_id, {"id": model_id, "display_name": model_id, "weight": 1, "role": "reviewer"})
            votes.append(Vote.from_json(payload, model, task["task_id"]))
        if not votes:
            print_warning(f"{task['task_id']} 没有有效 vote，跳过。")
            continue
        aggregates[task["task_id"]] = aggregate_votes(votes, config)
    print_info("merge 结果：")
    for task_id, aggregate in aggregates.items():
        print(f"- {task_id}: {aggregate.severity} · {aggregate.title} · votes={len(aggregate.votes)}")
    if args.dry_run or not args.apply:
        return 0

    warnings = git_preflight(root, config, True)
    for warning in warnings:
        print_warning(warning)
    validate_issue_notes(review_dir)

    units_by_id = {task["task_id"]: task_to_unit(root, task) for task in tasks}
    active_units = [units_by_id[task_id] for task_id in aggregates if task_id in units_by_id]
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
    for unit in active_units:
        aggregate = aggregates[unit.unit_id]
        open_existing = [
            item for item in existing_issues
            if item.get("source_unit_id") == unit.unit_id and item.get("status") in {"Open", "Unknown"}
        ]
        if aggregate.severity == "Correct":
            for item in open_existing:
                planned_moves.append((item["path"], issue_move_target(review_dir, item["path"], "Closed"), "Closed", item["id"]))
            continue
        if aggregate.severity in ISSUE_SEVERITIES:
            for item in open_existing:
                planned_moves.append((item["path"], issue_move_target(review_dir, item["path"], "Superseded"), "Superseded", item["id"]))
            issue_id = next_issue_id(issue_ledger)
            path = issue_path(review_dir, issue_id, aggregate.severity, aggregate.title)
            issue_links.setdefault(unit.unit_id, []).append((issue_id, path.relative_to(root)))
            planned_issue_text[path] = render_issue(unit, issue_id, aggregate, path, root)
            issue_ledger.setdefault("issues", {})[issue_id] = {
                "status": "unknown" if aggregate.severity == "Unknown" else "open",
                "severity": aggregate.severity,
                "source_file": unit.rel_path,
                "source_unit_id": unit.unit_id,
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
        updated = replace_ai_blocks_for_file(path, units, aggregates, issue_links)
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
    for path in files:
        all_units.extend(split_units(path, root, unit_ledger))
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


def serialize_unit_for_host(root: Path, unit: ReviewUnit, config: dict[str, Any], warning_keys: set[str]) -> dict[str, Any]:
    context_notes = build_context_notes(root, unit, config, warning_keys)
    return {
        "unit_id": unit.unit_id,
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
        "content": unit.content,
        "prompt": build_prompt(unit, context_notes),
    }


def host_prepare_payload(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    ensure_review_dirs(root, review_dir)
    warning_keys: set[str] = set()
    warnings = git_preflight(root, config, False)
    for warning in warnings:
        print_warning(warning)
    validate_issue_notes(review_dir)
    unit_ledger = load_json(review_dir / ".state" / "review-unit-ledger.json", {"version": 1, "next_unit_id": 1, "units": {}})
    files, units = discover_units_for_args(root, config, review_dir, args, unit_ledger)
    payload = {
        "version": 1,
        "kind": "ai-review-host-current-prepare",
        "created_at": _dt.datetime.now().isoformat(),
        "repo_root": str(root),
        "review_dir": str(review_dir.relative_to(root).as_posix()),
        "mode": {
            "scope": "all" if getattr(args, "all", False) else "changed",
            "dry_run": bool(getattr(args, "dry_run", False) or not getattr(args, "apply", False)),
            "apply": bool(getattr(args, "apply", False)),
            "limit": getattr(args, "limit", None),
            "issue": getattr(args, "issue", None),
            "paths": getattr(args, "paths", []),
        },
        "model_protocol": "AI-Review/MODEL_PROTOCOL.md",
        "output_contract": {
            "format": "JSON object or array",
            "accepted_shapes": [
                "数组：每项是一个单模型投票对象",
                "对象：{unit_id: vote_object}",
                "单对象：包含 unit_id 的 vote_object",
            ],
            "required_model_id": "host-current",
            "required_model_role": "main",
        },
        "files": [p.relative_to(root).as_posix() for p in files],
        "units": [serialize_unit_for_host(root, unit, config, warning_keys) for unit in units],
        "warnings": sorted(warning_keys),
    }
    return review_dir, payload


def command_prepare_host(args: argparse.Namespace) -> int:
    review_dir, payload = host_prepare_payload(args)
    output = Path(args.output) if args.output else review_dir / ".state" / "host-current-prepare.json"
    write_json_atomic(output, payload)
    print_info(f"host-current prepare 已生成：{output}")
    print_info(f"待当前会话模型审查 ReviewUnit：{len(payload['units'])}")
    if args.print_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def command_merge_host(args: argparse.Namespace) -> int:
    if not args.host_current_vote_file:
        raise AiReviewError("merge-host 需要 --host-current-vote-file。")
    prepare_payload: dict[str, Any] = {}
    if args.prepare_file:
        prepare_payload = load_json(Path(args.prepare_file), {})
    mode_data = prepare_payload.get("mode", {}) if isinstance(prepare_payload, dict) else {}
    ns = argparse.Namespace(
        command="review",
        changed=not bool(args.all or mode_data.get("scope") == "all"),
        all=bool(args.all or mode_data.get("scope") == "all"),
        paths=args.paths or mode_data.get("paths", []),
        issue=args.issue or mode_data.get("issue"),
        resume=False,
        dry_run=bool(args.dry_run or (not args.apply and mode_data.get("dry_run", True))),
        apply=bool(args.apply or mode_data.get("apply", False)),
        limit=args.limit if args.limit is not None else mode_data.get("limit"),
        main="host-current",
        host_current_vote_file=args.host_current_vote_file,
        no_external=bool(args.no_external),
        model_timeout=args.model_timeout,
        model_retry=args.model_retry,
        stream_total_timeout=args.stream_total_timeout,
    )
    return command_review(ns)


def command_review(args: argparse.Namespace) -> int:
    # 中文说明：review 是唯一写入入口。prepare-host/merge-host 最终也会
    # 回到这里，因此 issue 生命周期、Dashboard 和 ledger 只维护一份逻辑。
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    ensure_review_dirs(root, review_dir)
    secrets = load_yaml(root / ".ai-review-secrets.yaml")
    warning_keys: set[str] = set()
    warnings = git_preflight(root, config, bool(args.apply))
    for warning in warnings:
        print_warning(warning)
    validate_issue_notes(review_dir)

    unit_ledger_path = review_dir / ".state" / "review-unit-ledger.json"
    issue_ledger_path = review_dir / ".state" / "issue-ledger.json"
    unit_ledger = load_json(unit_ledger_path, {"version": 1, "next_unit_id": 1, "units": {}})
    issue_ledger = load_json(issue_ledger_path, {"version": 1, "next_issue_id_hex": "0001", "issues": {}})

    files, all_units = discover_units_for_args(root, config, review_dir, args, unit_ledger)
    if args.apply:
        save_run_state(review_dir, {"version": 1, "active_run": {"stage": "SCANNING", "started_at": _dt.datetime.now().isoformat(), "units": len(all_units)}, "last_runs": []})
    print_info(f"扫描到 {len(files)} 个 Markdown 文件，待审查 ReviewUnit：{len(all_units)}")

    link_index = build_link_index(all_units)
    host_votes = load_host_votes(args.host_current_vote_file)
    existing_issues = collect_issues(review_dir)
    aggregates: dict[str, AggregateResult] = {}
    issue_links: dict[str, list[tuple[str, Path]]] = {}
    planned_issue_text: dict[Path, str] = {}
    planned_moves: list[tuple[Path, Path, str, str]] = []
    if args.apply:
        save_run_state(review_dir, {"version": 1, "active_run": {"stage": "VOTING", "units": len(all_units)}, "last_runs": []})

    for idx, unit in enumerate(all_units, start=1):
        context_notes = build_context_notes(root, unit, config, warning_keys)
        votes = collect_votes(unit, config, secrets, args, context_notes, host_votes, warning_keys)
        if not votes:
            print_warning(f"{unit.unit_id} 没有任何成功模型投票，跳过；失败模型不生成 Unknown 票。")
            continue
        aggregate = aggregate_votes(votes, config)
        aggregates[unit.unit_id] = aggregate
        open_existing = [
            item for item in existing_issues
            if item.get("source_unit_id") == unit.unit_id and item.get("status") in {"Open", "Unknown"}
        ]
        if aggregate.severity == "Correct":
            for item in open_existing:
                src = item["path"]
                dst = issue_move_target(review_dir, src, "Closed")
                planned_moves.append((src, dst, "Closed", item["id"]))
            print_info(f"{idx}/{len(all_units)} {unit.unit_id} {unit.rel_path}:{unit.start_line} -> {aggregate.severity}")
            continue
        if aggregate.severity in ISSUE_SEVERITIES:
            for item in open_existing:
                src = item["path"]
                dst = issue_move_target(review_dir, src, "Superseded")
                planned_moves.append((src, dst, "Superseded", item["id"]))
            issue_id = next_issue_id(issue_ledger)
            path = issue_path(review_dir, issue_id, aggregate.severity, aggregate.title)
            issue_links.setdefault(unit.unit_id, []).append((issue_id, path.relative_to(root)))
            planned_issue_text[path] = render_issue(unit, issue_id, aggregate, path, root)
            issue_ledger.setdefault("issues", {})[issue_id] = {
                "status": "unknown" if aggregate.severity == "Unknown" else "open",
                "severity": aggregate.severity,
                "source_file": unit.rel_path,
                "source_unit_id": unit.unit_id,
                "content_hash": unit.content_hash,
                "path": path.relative_to(root).as_posix(),
                "created_at": now_date(),
            }
        print_info(f"{idx}/{len(all_units)} {unit.unit_id} {unit.rel_path}:{unit.start_line} -> {aggregate.severity}")

    if args.dry_run or not args.apply:
        print_info("dry-run 结果：")
        for unit_id, aggregate in aggregates.items():
            print(f"- {unit_id}: {aggregate.severity} · {aggregate.title} · votes={len(aggregate.votes)}")
        for src, dst, status, issue_id in planned_moves:
            print(f"- move {issue_id}: {src.relative_to(root).as_posix()} -> {dst.relative_to(root).as_posix()} ({status})")
        return 0

    save_run_state(review_dir, {"version": 1, "active_run": {"stage": "WRITING", "units": len(aggregates)}, "last_runs": []})
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
    for unit in all_units:
        if unit.unit_id in aggregates:
            by_file.setdefault(unit.file_path, []).append(unit)
    for path, units in by_file.items():
        updated = replace_ai_blocks_for_file(path, units, aggregates, issue_links)
        write_text_atomic(path, updated)
    write_json_atomic(unit_ledger_path, unit_ledger)
    write_json_atomic(issue_ledger_path, issue_ledger)
    write_json_atomic(review_dir / ".state" / "link-index.json", link_index)
    write_json_atomic(review_dir / ".state" / "model-warning-ledger.json", {"version": 1, "warnings": sorted(warning_keys)})
    write_text_atomic(review_dir / "Dashboard.md", render_dashboard(review_dir, int(deep_get(config, "dashboard.top_n_per_section", 10))))
    for warning in validate_markdown_and_links(root, list(planned_issue_text) + list(by_file)):
        print_warning(warning)
    diff = run_git(["diff", "--stat"], root)
    print(diff.stdout.rstrip())
    save_run_state(review_dir, {"version": 1, "active_run": None, "last_runs": [{"mode": "apply", "finished_at": _dt.datetime.now().isoformat(), "units": len(aggregates)}]})
    print_info("写入完成。")
    return 0


def validate_frontmatter_text(text: str) -> None:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise AiReviewError("frontmatter 校验失败。")
    if text.count("<!-- user-notes:start -->") != 1 or text.count("<!-- user-notes:end -->") != 1:
        raise AiReviewError("人工备注区校验失败。")


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


def command_resume(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config = load_yaml(root / ".ai-review.yaml")
    review_dir = root / str(config.get("review_dir", "AI-Review"))
    state = load_json(review_dir / ".state" / "run-state.json", {"version": 1, "active_run": None, "last_runs": []})
    if not state.get("active_run"):
        print_info("没有可恢复的 active_run。")
        return 0
    print_info(f"检测到未完成 run：{json.dumps(state['active_run'], ensure_ascii=False)}")
    ns = argparse.Namespace(**vars(args))
    ns.resume = False
    ns.changed = True
    ns.all = False
    ns.paths = []
    ns.issue = None
    return command_review(ns)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-review", description="AI Review CLI")
    sub = parser.add_subparsers(dest="command")
    review = sub.add_parser("review", help="审查 Markdown ReviewUnit")
    scope = review.add_mutually_exclusive_group()
    scope.add_argument("--changed", action="store_true", help="只审查 Git 变更文件")
    scope.add_argument("--all", action="store_true", help="审查全仓库")
    review.add_argument("paths", nargs="*", help="指定文件或目录")
    review.add_argument("--issue", help="复查指定 issue")
    review.add_argument("--resume", action="store_true", help="恢复上次运行")
    mode = review.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    mode.add_argument("--apply", action="store_true", help="事务化写入")
    review.add_argument("--limit", type=int, help="最多审查 N 个 ReviewUnit")
    review.add_argument("--main", choices=["host-current", "configured", "none"], help="覆盖主模型模式")
    review.add_argument("--host-current-vote-file", help="注入 host-current 主模型投票 JSON")
    review.add_argument("--no-external", action="store_true", help="不调用外部 voter API，仅验证扫描、聚合和渲染路径")
    review.add_argument("--model-timeout", type=int, help="临时覆盖单次外部模型请求超时秒数")
    review.add_argument("--model-retry", type=int, help="临时覆盖外部模型重试次数")
    review.add_argument("--stream-total-timeout", type=int, help="临时覆盖单次流式响应总时长上限秒数")

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

    prepare = sub.add_parser("prepare-host", help="为 Codex/Cursor 当前会话模型准备 host-current 审查输入")
    prepare_scope = prepare.add_mutually_exclusive_group()
    prepare_scope.add_argument("--changed", action="store_true", help="只准备 Git 变更文件")
    prepare_scope.add_argument("--all", action="store_true", help="准备全仓库")
    prepare.add_argument("paths", nargs="*", help="指定文件或目录")
    prepare.add_argument("--issue", help="准备复查指定 issue")
    prepare.add_argument("--limit", type=int, help="最多准备 N 个 ReviewUnit")
    prepare_mode = prepare.add_mutually_exclusive_group()
    prepare_mode.add_argument("--dry-run", action="store_true", help="准备 dry-run 审查")
    prepare_mode.add_argument("--apply", action="store_true", help="准备 apply 审查")
    prepare.add_argument("--output", help="prepare JSON 输出路径，默认 AI-Review/.state/host-current-prepare.json")
    prepare.add_argument("--print-json", action="store_true", help="同时向 stdout 打印完整 JSON")

    merge = sub.add_parser("merge-host", help="合并 Codex/Cursor 当前会话模型投票并继续 CLI 流程")
    merge_scope = merge.add_mutually_exclusive_group()
    merge_scope.add_argument("--changed", action="store_true", help="只审查 Git 变更文件")
    merge_scope.add_argument("--all", action="store_true", help="审查全仓库")
    merge.add_argument("paths", nargs="*", help="指定文件或目录")
    merge.add_argument("--issue", help="复查指定 issue")
    merge_mode = merge.add_mutually_exclusive_group()
    merge_mode.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    merge_mode.add_argument("--apply", action="store_true", help="事务化写入")
    merge.add_argument("--limit", type=int, help="最多审查 N 个 ReviewUnit")
    merge.add_argument("--prepare-file", default="AI-Review/.state/host-current-prepare.json", help="prepare-host 生成的 JSON")
    merge.add_argument("--host-current-vote-file", required=True, help="当前会话模型生成的投票 JSON")
    merge.add_argument("--no-external", action="store_true", help="不调用外部 voter API，仅使用 host-current 投票")
    merge.add_argument("--model-timeout", type=int, help="临时覆盖单次外部模型请求超时秒数")
    merge.add_argument("--model-retry", type=int, help="临时覆盖外部模型重试次数")
    merge.add_argument("--stream-total-timeout", type=int, help="临时覆盖单次流式响应总时长上限秒数")

    dashboard = sub.add_parser("dashboard", help="更新 Dashboard")
    dashboard.add_argument("--dry-run", action="store_true")
    sub.add_parser("check", help="检查配置、状态和链接")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        args = parser.parse_args(["review", "--changed", "--dry-run"])
    try:
        if args.command == "review":
            if getattr(args, "resume", False):
                return command_resume(args)
            if not args.dry_run and not args.apply:
                default = load_yaml(Path.cwd() / ".ai-review.yaml").get("default_mode", {})
                args.dry_run = bool(default.get("dry_run", True))
                if not args.changed and not args.all and not args.paths:
                    args.changed = str(default.get("scope", "changed")) == "changed"
            return command_review(args)
        if args.command == "vote":
            return command_vote_tasks(args)
        if args.command == "merge":
            if not args.dry_run and not args.apply:
                default = load_yaml(Path.cwd() / ".ai-review.yaml").get("default_mode", {})
                args.dry_run = bool(default.get("dry_run", True))
            return command_merge_tasks(args)
        if args.command == "prepare-host":
            if not args.dry_run and not args.apply:
                default = load_yaml(Path.cwd() / ".ai-review.yaml").get("default_mode", {})
                args.dry_run = bool(default.get("dry_run", True))
                if not args.changed and not args.all and not args.paths:
                    args.changed = str(default.get("scope", "changed")) == "changed"
            return command_prepare_host(args)
        if args.command == "merge-host":
            return command_merge_host(args)
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
