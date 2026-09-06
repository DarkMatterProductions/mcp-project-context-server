# ADR-00012: Targeted tools for ADR and project.md access

## Status
Accepted

## Context

`load_project_context` currently returns the full content of `project.md`, all ADR files, and the latest session summary in a single response. In practice this output regularly exceeds what can be held in an LLM's active context window — the tool response for this project was 56.2 KB, which had to be saved to a temp file and could not be read in full. The calling agent silently fell back to direct file system reads to answer a basic question about the project's ADRs.

This is a structural problem: a tool designed as the primary session entry point is producing output that cannot be consumed by the agent it is designed to serve. The root cause is that the tool couples *session initialization* (load `project.md` so the agent knows what project it is in) with *bulk content delivery* (return every ADR verbatim). These are two distinct needs and should not be handled by the same operation.

The solution is a set of targeted, single-purpose tools that allow an agent to fetch exactly what it needs, when it needs it — rather than receiving everything upfront and hoping it fits in context.

**ADR-00010 superseded.** ADR-00010 independently proposed an overlapping tool set for ADR lifecycle management (listing, status/section reads, status transitions, creation with sequential numbering) and left its `Decision`/`Consequences`/`Alternatives Considered` unresolved. Rather than finalize two separately-accepted ADRs that name the same operations differently (`search_adrs` vs. `search_adr`, `create_adr` vs. `write_adr`, `update_adr_section` vs. `edit_adr`), this ADR absorbs ADR-00010's resolved design (sequential numbering, status-transition validation, section addressing) under this ADR's naming, and ADR-00010 is marked `Superseded by ADR-00012`. ADR-00010's citation of an "ADR-00000 template" file was also found to be stale — no such file exists; the template lives in `.context/adr-creation-and-review-process.md`.

Two tools originally proposed by either ADR turned out to already exist under different names, discovered during this review: `search_adr_index` (semantic, ADR-scoped search) already implements "Search ADRs"/`search_adr`, and `load_context_files` (generic tagged full-file read by path) already implements `read_adr`/`read_project` for callers that know the exact path.

## Decision

**Discovery / read tools (no write access):**

- `list_adrs(project_path)` — lightweight structural listing of every file in `.context/decisions/`: number, title, status, filename. Built on the existing `list_context_files(project_path, "decisions/")` helper plus a per-file parse of the `# ADR-XXXXX: Title` line and the `## Status` field. Requires no vector index, so it's usable even before/without `index_project_context`.
- `read_adr(project_path, number_or_filename)` — resolves an ADR number (e.g. `12`) or filename via `list_adrs`, then returns the full raw markdown using the same `resolve_requested_files`/`format_tagged_file` machinery `load_context_files` already uses. Exists for number-based lookup convenience and to guarantee the target is actually a `.context/decisions/` file; a caller that already knows the exact filename can use `load_context_files` directly.
- `read_adr_status(project_path, number_or_filename)` — returns only the parsed `## Status` value and title, without the rest of the file.
- `list_adr_sections(project_path, number_or_filename)` — returns the ordered top-level section list for one ADR (whichever of `Status`/`Context`/`Decision`/`Consequences`/`Alternatives Considered`/etc. it actually has). Section boundaries follow ADR-00007's heading-boundary rule (top-level `##` only).
- `read_adr_section(project_path, number_or_filename, section)` — returns one named top-level section's content.
- `search_adr_sections(project_path, number_or_filename, query, n_results)` — semantic search scoped to a single ADR's own sections, via the existing vector store/embedding pipeline filtered to that ADR's file *and* section. Depends on chunk metadata carrying a `section` field (see Consequences).
- Cross-ADR semantic search and whole-`project.md` reads are **not** redefined here — they remain `search_adr_index` and `load_context_files` respectively, both already implemented.

**Write tools (mutating, always section-addressed — never by line/byte offset):**

- `create_adr(project_path, title, context)` — scaffolds a new ADR: allocates the next sequential number under a lock (scans `.context/decisions/` for the highest existing `ADR-XXXXX` number, increments; malformed filenames are ignored for allocation and returned as warnings; starts at `ADR-00001` if none exist), fills the template with `Status: Proposed`, the given title/Context, and placeholder Decision/Consequences/Alternatives Considered.
- `edit_adr(project_path, number_or_filename, section, content)` — replaces one named top-level section, leaving the rest of the file untouched. **Cannot target `## Status`** — status changes must go through `update_adr_status` so lifecycle side effects can't be bypassed by a generic edit.
- `update_adr_status(project_path, number_or_filename, new_status, explanation=None)` — dedicated status-transition tool, deliberately kept separate from `edit_adr`: validates the transition against known status values and the expected flow (`Proposed → Under Review → Accepted → Implemented/Deprecated/Superseded by ADR-XXXXX`); unusual transitions require `explanation` and are warned-but-allowed rather than blocked. While `Proposed`/`Under Review`, `explanation` is appended to `ADR Review Discussion`. Transitioning to `Accepted` requires a populated `Decision` section, moves any `explanation` into `Decision` as transition rationale, removes `ADR Review Discussion` entirely, and only then writes the new status — failing with an actionable error if `Decision` is empty.
- `write_project(project_path, content)` — fully replaces `project.md`.
- `edit_project(project_path, section, content)` — replaces one named top-level section of `project.md`, leaving the rest untouched.

**Remote-write policy (extends ADR-00022's pattern to ADR/project.md writes):**

All five write tools route through the same `RepositoryProvider.write_file(..., branch=...)`/`create_branch(...)` machinery `save_session_summary` already uses. `LocalRepositoryProvider` (`REPO_PROVIDER` unset/`"local"`, the default) ignores `branch`, identical to today's behavior — no change for local/default deployments.

For a remote provider (`REPO_PROVIDER` set to `github`/`gitlab`/`gitea`), a new `REPO_ADR_WRITE_MODE` env var controls targeting, **defaulting to `"branch"`** — the inverse of `REPO_SESSION_WRITE_MODE`'s `"direct"` default — because an ADR or `project.md` write is an architectural-record change, not an ephemeral session note, and should land for review by default. Branches are named `mcp-adr/{date}-{HHMMSS}`, mirroring `save_session_summary`'s `mcp-session/...` convention. Set `REPO_ADR_WRITE_MODE=direct` to opt out. This is one setting governing all five write tools uniformly, consistent with every other `REPO_*` setting being a deployment-level policy rather than a per-call LLM choice.

**Reindexing:** none of the write tools auto-reindex by default; each accepts an optional `auto_reindex: bool = False` to trigger `index_project_context` afterward. Otherwise, responses note that a manual reindex is needed for search freshness.

## Consequences

- One coherent, non-overlapping tool surface for ADR + `project.md` access, replacing two independently-drafted and partially-conflicting ADRs.
- Two tools either ADR originally proposed (`search_adrs`/`search_adr`, `read_project`) are **not** built — `search_adr_index` and `load_context_files` already satisfy them — so the implementation surface is smaller than either ADR alone implied.
- `list_adr_sections`/`read_adr_section`/`search_adr_sections` depend on ADR-00007's heading-boundary chunking, which is `Accepted` but **not yet implemented** (`indexing/indexer.py` still does fixed-size chunking). Implementing this ADR requires: (a) factoring section-splitting into a shared helper usable by both `indexing/indexer.py` and these read tools, and (b) extending ADR-00007's chunk metadata to carry a `section` field, which ADR-00007 doesn't currently specify.
- Several existing ADRs (ADR-00014–00019, ADR-00022) use `**Status:** X`/`**Date:**`/`**Author:**` inline-bold metadata instead of the template's `## Status` heading. `list_adrs`/`read_adr_status`/section tools must tolerate both formats, or those files must be normalized to the canonical template first. Not addressed by this ADR — flagged as a required follow-up before these tools are reliable across the *entire* ADR set, not just newly-created ones.
- New `REPO_ADR_WRITE_MODE` env var (default `branch` for remote providers, `direct` to opt out; ignored for local) — deliberately different default than `REPO_SESSION_WRITE_MODE` given the higher stakes of architectural-record changes.
- Five new tool files under `tools/`, a shared section-parsing helper, and `REPO_ADR_WRITE_MODE` plumbing in the repository providers — additive per ADR-00004's modular architecture; no existing tool file needs modification besides `server.py`'s registration lists.

## Alternatives Considered

- **Increase the output limit on `load_project_context`**: rejected — shifts the overflow threshold rather than eliminating it; a project with 50 ADRs overflows any fixed limit.
- **Return only ADR summaries (title + status) from `load_project_context`**: rejected — still couples initialization with content delivery; an agent needing no ADR context still pays the summary-fetch cost.
- **Expose raw file system tools (`read_file`/`write_file`)**: rejected — overly general; agents would need to know `.context/` structure, naming conventions, and template requirements that purpose-built tools already encode.
- **Extend `search_adr_index` itself instead of adding section/status tools**: rejected — that tool is vector-similarity search, appropriate for semantic queries; deterministic reads (exact status, exact section, exact file) need deterministic file access, not similarity ranking.
- **Keep ADR-00010 and ADR-00012 as two separately-accepted decisions**: rejected — they name overlapping operations differently, and ADR-00012 already declared intent to supersede ADR-00010's naming; keeping both invites the ambiguity ADRs exist to prevent.
- **Fold status transitions into `edit_adr` as a special-cased section**: rejected — would let `edit_adr("Status", "Accepted")` silently skip the required Decision-population/Review-Discussion-removal side effects; a dedicated tool keeps lifecycle enforcement as the only path to `Accepted`.
- **Default `REPO_ADR_WRITE_MODE` to `direct` (matching `REPO_SESSION_WRITE_MODE`)**: rejected per explicit direction — architectural-record changes should default to a review branch; operators wanting unreviewed direct writes opt in via `direct`.
- **Build a dual-format Status parser tolerant of both `## Status` and `**Status:**` styles**: deferred, not resolved here — normalizing the 7 legacy-format ADRs is unrelated cleanup outside this ADR's scope; noted in Consequences as a follow-up.
