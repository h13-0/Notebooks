from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any


DEFAULT_EXCLUDED_PARTS = {
    ".git",
    ".obsidian",
    ".codex",
    ".cursor",
    "__pycache__",
}


def _config_list(config: dict[str, Any], key: str) -> list[str]:
    cur: Any = config
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return []
        cur = cur[part]
    if cur is None:
        return []
    if isinstance(cur, str):
        return [cur]
    if isinstance(cur, list):
        return [str(item).replace("\\", "/").strip("/") for item in cur if str(item).strip()]
    return []


def configured_excludes(config: dict[str, Any], review_dir: Path, root: Path) -> tuple[set[str], list[str]]:
    """Return directory-name and glob excludes from config.

    中文说明：扫描黑名单分两层处理。简单目录名进入 parts 集合，
    带通配符或多级路径的规则进入 glob 列表，用于匹配仓库相对路径。
    """
    parts = set(DEFAULT_EXCLUDED_PARTS)
    globs: list[str] = []
    try:
        review_name = review_dir.relative_to(root).parts[0]
    except ValueError:
        review_name = review_dir.name
    parts.add(review_name)
    for item in _config_list(config, "scan.exclude_paths"):
        normalized = item.replace("\\", "/").strip("/")
        if not normalized:
            continue
        if "/" in normalized or "*" in normalized or "?" in normalized or "[" in normalized:
            globs.append(normalized)
        else:
            parts.add(normalized)
    return parts, globs


def is_path_excluded(path: Path, root: Path, excluded_parts: set[str], excluded_globs: list[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    if any(part in excluded_parts for part in path.relative_to(root).parts):
        return True
    for pattern in excluded_globs:
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(rel + "/", pattern.rstrip("/") + "/"):
            return True
    return False

