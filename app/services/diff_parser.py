from pathlib import Path
from typing import Any

from unidiff import PatchSet
from unidiff.errors import UnidiffParseError


LANGUAGE_BY_SUFFIX = {
    ".css": "css",
    ".go": "go",
    ".html": "html",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "javascript",
    ".md": "markdown",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".sh": "shell",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".txt": "text",
    ".yaml": "yaml",
    ".yml": "yaml",
}

LANGUAGE_BY_NAME = {
    "dockerfile": "dockerfile",
    "makefile": "makefile",
}


def parse_diff(raw_diff: str) -> list[dict[str, Any]]:
    try:
        patch = PatchSet(raw_diff.splitlines(keepends=True))
    except UnidiffParseError as exc:
        return [
            {
                "path": "__error__",
                "change_kind": "modified",
                "hunks": [f"failed to parse diff: {exc}"],
                "language_or_kind": "unknown",
            }
        ]

    return [_parse_file(file) for file in patch]


def _parse_file(file: Any) -> dict[str, Any]:
    path = _file_path(file)

    return {
        "path": path,
        "change_kind": _change_kind(file),
        "hunks": [str(hunk) for hunk in file],
        "language_or_kind": _language_or_kind(path),
    }


def _change_kind(file: Any) -> str:
    if file.is_added_file:
        return "added"
    if file.is_removed_file:
        return "removed"
    if file.is_rename:
        return "renamed"
    return "modified"


def _file_path(file: Any) -> str:
    if file.is_removed_file:
        return _clean_git_path(file.source_file)
    return _clean_git_path(file.target_file or file.path)


def _clean_git_path(path: str) -> str:
    if path == "/dev/null":
        return path
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def _language_or_kind(path: str) -> str:
    name = Path(path).name.lower()
    if name in LANGUAGE_BY_NAME:
        return LANGUAGE_BY_NAME[name]
    return LANGUAGE_BY_SUFFIX.get(Path(path).suffix.lower(), "unknown")
