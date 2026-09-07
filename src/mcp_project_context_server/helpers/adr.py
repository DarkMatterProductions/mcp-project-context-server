"""ADR discovery, resolution, and section-editing helpers, shared by the ``*_adr*`` tools.

Naming convention (from ``.context/adr-creation-and-review-process.md``):
``ADR-XXXXX-{kebab-case-topic}.md``, zero-padded to 5 digits, sequential, never
reused. Files that don't match this convention are excluded from `list_adrs`'s
results and reported as warnings instead.
"""
import re
from dataclasses import dataclass

from mcp_project_context_server.helpers.context_files import list_context_files, resolve_requested_files
from mcp_project_context_server.helpers.sections import Section, split_sections

_FILENAME_RE = re.compile(r"^ADR-(\d{5})-.*\.md$")
_TITLE_RE = re.compile(r"^#(?!#)[ \t]+ADR-\d+:\s*(.+)$", re.MULTILINE)


@dataclass
class AdrInfo:
    """Structural metadata about one ADR file.

    :ivar malformed: True when the title or ``## Status`` section could not be
        parsed (e.g. the legacy ``**Status:**`` inline format used by several
        older ADRs), even though the filename itself matched the naming convention.
    """

    number: int
    filename: str
    path: str
    title: str
    status: str | None
    malformed: bool


@dataclass
class AdrResolution:
    """Result of resolving a number/filename to an ADR, or a not-found explanation."""

    info: AdrInfo | None
    content: str | None
    error: str | None


async def list_adrs(project_path: str) -> tuple[list[AdrInfo], list[str]]:
    """List every well-named ADR under ``decisions/``, sorted by number.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :return: (tuple) ``(infos, warnings)`` — parsed `AdrInfo` entries in ascending
        number order, and human-readable warnings for filenames that don't match
        the ``ADR-XXXXX-*.md`` convention (excluded from `infos`) or that could
        not be read.
    """
    paths = await list_context_files(project_path, "decisions/")
    warnings: list[str] = []

    candidates: list[tuple[str, str, int]] = []
    for path in paths:
        filename = path.rsplit("/", 1)[-1]
        match = _FILENAME_RE.match(filename)
        if not match:
            warnings.append(f"Skipped '{path}': filename does not match the ADR-XXXXX-*.md convention.")
            continue
        candidates.append((path, filename, int(match.group(1))))

    found, missing = await resolve_requested_files(project_path, [path for path, _, _ in candidates])
    for path in missing:
        warnings.append(f"Could not read '{path}'.")

    infos: list[AdrInfo] = []
    for path, filename, number in candidates:
        content = found.get(path)
        if content is None:
            continue
        title_match = _TITLE_RE.search(content)
        title = title_match.group(1).strip() if title_match else ""
        status, status_found = parse_status(content)
        infos.append(
            AdrInfo(
                number=number,
                filename=filename,
                path=path,
                title=title,
                status=status,
                malformed=not status_found or not title,
            )
        )

    infos.sort(key=lambda info: info.number)
    return infos, warnings


def _match_adr(infos: list[AdrInfo], number_or_filename: str | int) -> AdrInfo | None:
    if isinstance(number_or_filename, int):
        return next((info for info in infos if info.number == number_or_filename), None)

    raw = str(number_or_filename).strip()
    if raw.isdigit():
        return next((info for info in infos if info.number == int(raw)), None)

    short_match = re.match(r"^ADR-(\d+)$", raw, re.IGNORECASE)
    if short_match:
        return next((info for info in infos if info.number == int(short_match.group(1))), None)

    return next((info for info in infos if info.filename == raw or info.path == raw), None)


async def resolve_adr(project_path: str, number_or_filename: str | int) -> AdrResolution:
    """Resolve a bare number, ``ADR-XXXXX`` short form, or exact filename to its content.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param number_or_filename: (str|int) An ADR number (``12`` or ``"12"``), short
        form (``"ADR-00012"``), or exact filename/path under ``decisions/``.
    :return: (AdrResolution) The matched `AdrInfo` and its content, or an `error`
        message listing the known ADRs when nothing matches.
    """
    infos, _warnings = await list_adrs(project_path)
    target = _match_adr(infos, number_or_filename)
    if target is None:
        known = ", ".join(f"ADR-{info.number:05d}" for info in infos) or "none"
        return AdrResolution(
            info=None,
            content=None,
            error=f"No ADR found matching '{number_or_filename}'. Known ADRs: {known}.",
        )

    found, _missing = await resolve_requested_files(project_path, [target.path])
    content = found.get(target.path)
    if content is None:
        return AdrResolution(info=target, content=None, error=f"Could not read '{target.path}'.")

    return AdrResolution(info=target, content=content, error=None)


def parse_status(content: str) -> tuple[str, bool]:
    """Parse the value of an ADR's ``## Status`` section.

    :param content: (str) The ADR's full markdown content.
    :return: (tuple) ``(status, found)``. ``found`` is False when no ``## Status``
        heading exists at all — the signal that this ADR uses the legacy
        ``**Status:**`` inline format, which callers should report as unsupported
        rather than silently misreading.
    """
    section = find_section(content, "Status")
    if section is None:
        return "", False

    for line in section.content.splitlines()[1:]:
        stripped = line.strip()
        if stripped:
            return stripped, True

    return "", True


def find_section(content: str, section_name: str) -> Section | None:
    """Find a top-level (``##``) section by exact name.

    :param content: (str) The full markdown document content.
    :param section_name: (str) The exact heading text to match.
    :return: (Section|None) The matching section, or None if not present.
    """
    for section in split_sections(content):
        if section.name == section_name:
            return section
    return None


def replace_section(content: str, section_name: str, new_content: str) -> str | None:
    """Rebuild *content* with one top-level section's body swapped in.

    :param content: (str) The full markdown document content.
    :param section_name: (str) The exact heading text of the section to replace.
    :param new_content: (str) The section's new body (heading excluded).
    :return: (str|None) The rebuilt document, or None if no section named
        *section_name* exists.
    """
    sections = split_sections(content)
    index = next((i for i, section in enumerate(sections) if section.name == section_name), None)
    if index is None:
        return None

    trailing = "\n" if index == len(sections) - 1 else "\n\n"
    new_section_text = f"## {section_name}\n\n{new_content.strip()}{trailing}"

    return "".join(new_section_text if i == index else section.content for i, section in enumerate(sections))
