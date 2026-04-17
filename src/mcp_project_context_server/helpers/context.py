"""Shared helpers for .context/ directory resolution and file reading."""

from pathlib import Path


def find_context_dir(project_path: str | Path) -> Path | None:
    """Walk up from project_path to find a .context/ directory."""
    p = Path(project_path).resolve()
    for candidate in [p, *p.parents]:
        ctx = candidate / ".context"
        if ctx.is_dir():
            return ctx
    return None


def collection_name_for(context_dir: Path) -> str:
    """Derive a stable ChromaDB collection name from the project root.

    Always based on context_dir.parent so it is consistent regardless of
    whether the caller passed a project root, a subdirectory, or a file path.
    """
    project_name = context_dir.parent.name
    return f"ctx_{project_name}".replace("-", "_").replace(" ", "_")[:63]


def read_context_files(context_dir: Path) -> dict[str, str]:
    """Read all markdown files from .context/ into a dict.

    Keys use POSIX-style forward slashes (Path.as_posix()) so that ChromaDB
    document IDs and metadata are identical on Windows and Linux.
    """
    return {md_file.relative_to(context_dir).as_posix(): md_file.read_text(encoding="utf-8") for md_file in context_dir.rglob("*.md")}
