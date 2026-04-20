# ADR-00008: POSIX path normalization for ChromaDB document IDs

## Status
Implemented

## Context

ChromaDB document IDs and metadata values are strings. File paths are used as document IDs to provide stable, unique identifiers for each chunk and to carry source file information as retrievable metadata.

On Windows, Python's `Path` object produces backslash-separated strings when converted with `str()`:

```python
str(Path("C:/Users/drahk/.context/decisions/ADR-00001-mcp-protocol.md"))
# → "C:\\Users\\drahk\\.context\\decisions\\ADR-00001-mcp-protocol.md"
```

On Linux/macOS, `str(Path(...))` produces forward-slash strings. This means a ChromaDB store built on Windows would contain document IDs that differ in path separator from the same store accessed on Linux — breaking any cross-platform consistency and making document IDs non-portable.

Additionally, `mcp-project-context-server` is intended to run on both Windows and non-Windows systems (it is developed on Windows, deployed alongside codebases on any platform).

## Decision

All ChromaDB document IDs and metadata values that contain file paths are normalized to POSIX format using `.as_posix()` before being passed to the ChromaDB API. `Path` objects are converted to strings only at the ChromaDB API boundary, not at any intermediate point.

This is implemented in `helpers/context.py` (`read_context_files()` returns a `dict[str, str]` where keys are `.as_posix()` strings) and in `indexing/chroma/indexer.py` (chunk document IDs and metadata `source` values use `.as_posix()`).

```python
# Correct — always forward slashes regardless of OS
doc_id = f"{path.as_posix()}::chunk::{chunk_idx}"
metadata = {"source": path.as_posix()}

# Wrong — OS-dependent
doc_id = f"{str(path)}::chunk::{chunk_idx}"
```

## Consequences

- Document IDs and metadata `source` values in ChromaDB are always forward-slash strings, regardless of the host OS.
- A collection indexed on Windows is compatible with queries run on Linux/macOS (and vice versa) — the document IDs will match.
- New code that adds or queries ChromaDB documents must follow the same convention. Using `str(Path(...))` at the ChromaDB boundary is a bug — it will produce platform-inconsistent IDs.
- The POSIX convention applies only to ChromaDB data. Internal Python code (`pathlib.Path` objects, `os.path` calls) continues to use native path semantics as appropriate.

## Alternatives Considered

- **`str(Path(...))`**: Rejected. OS-dependent output. Would produce `\\` separators on Windows, making document IDs non-portable.
- **`path.replace("\\", "/")`**: Rejected. Fragile — easy to miss at new call sites, and only fixes the backslash issue without providing the other normalization guarantees that `.as_posix()` provides (e.g., consistent drive letter handling on Windows).
- **Storing only the relative path (not absolute)**: Considered as a complementary measure. Relative paths from the `.context/` directory root would be shorter and more portable. Not yet implemented — would change the document ID format and require a re-index migration.
