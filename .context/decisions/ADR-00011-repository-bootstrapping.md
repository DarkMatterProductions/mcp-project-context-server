# ADR-00011: Repository bootstrapping tool

## Status

Accepted

## Context

Every new project that wants to use `mcp-project-context-server` must manually create the `.context/` directory structure before the server can do anything useful. The required structure is:

```
.context/
├── project.md       ← project overview (required by load_project_context)
├── decisions/       ← ADR directory (required by load_project_context)
└── sessions/        ← session notes (created on first save_session_summary call)
```

`project.md` is the most important file. The `load_project_context` tool reads it first, and it must follow the defined template structure (`# Project`, `## One-liner`, `## Tech Stack`, `## Architecture`, `## Key Conventions`, `## ADRs`, `## Current Active Work`, `## Known Pain Points / Tech Debt`, `## Entry Points`).

Today, this is a manual process. The user (or agent) must:
1. Create the `.context/` directory and subdirectories
2. Write a `project.md` conforming to the template
3. Call `index_project_context` to seed the vector store

The server is well-positioned to automate this. It already knows the required structure. It can inspect common project metadata files (`pyproject.toml`, `package.json`, `README.md`, `go.mod`, `Cargo.toml`) to extract project name, description, dependencies, and entry points — pre-filling the `project.md` template with real content rather than empty stubs.

This solves the chicken-and-egg problem: to use the context server effectively, you need a `.context/` directory; but creating that directory correctly requires understanding the template — which the server can provide automatically.

## Decision

We implemented a `bootstrap_context` tool that atomically creates a compliant `.context/` directory for any project, plus a companion `get_bootstrap_questions` tool that returns a reusable, extensible question registry for interview-driven content.

**Content resolution**: `project.md` content is populated through an interactive interview — `get_bootstrap_questions` returns the canonical question set (currently for the `project` target), the calling agent asks the user, and their answers are passed to `bootstrap_context` via `project_sections`. This supersedes automatic metadata-file inference entirely: there is no `pyproject.toml`/`package.json` parsing. Missing answers render as `[TBD]` placeholders (or a default ADR pointer for the `ADRs` section), so a partial interview still produces valid output.

**Idempotency**: all four file-level artifacts (`ADR_CREATE_AND_MANAGEMENT.md`, `PLANNING_LOOP.md`, `project.md`, and the governance ADR) are additive-only — an existing file is left untouched and reported as "skipped (already exists)"; only missing artifacts are created. This resolves the original "destructive vs. additive" and "idempotency" questions in favor of the safer, non-destructive default, with no "overwrite if skeleton-only" special case.

**Governance content**: `ADR_CREATE_AND_MANAGEMENT.md` and `PLANNING_LOOP.md` are verbatim copies of this project's own `.context/adr-creation-and-review-process.md` and `.context/development-cycle.md`, bundled as package resources under `src/mcp_project_context_server/templates/` and read via `importlib.resources`. Every bootstrapped project inherits the same ADR lifecycle and plan/propose/approve/implement cycle this project follows.

**Governance ADR**: `bootstrap_context` creates ADR-00001 ("Consistent Use of Architecture Decision Records in the Standard Development Cycle") by delegating to the existing `create_adr` tool, landing with `Status: Proposed` — like any other ADR, left for the user to review and accept, not force-accepted by the bootstrap step. If any ADR already exists in the target project, this step is skipped entirely, regardless of that ADR's topic.

**Implementation reuse**: rather than duplicating file-write/branch logic, `bootstrap_context` delegates `project.md` writing to `write_project.handle()` and the governance ADR to `create_adr.handle()`, both called with `auto_reindex: False`. `bootstrap_context` issues exactly one `append_reindex_note` call at the end, driven by its own `auto_reindex` argument, so a single reindex reminder (or single actual reindex run) covers the whole operation instead of one per delegated call.

**Directory creation**: for local targets, `.context/`, `.context/decisions/`, and `.context/sessions/` are created directly (bypassing `find_context_dir`, which only locates an *existing* `.context/` and cannot bootstrap a new one) before any delegated write. For remote targets, directories are not created explicitly — git repositories have no empty-directory concept — so `decisions/` appears on first ADR write and `sessions/` remains absent until the first `save_session_summary` call, consistent with that tool's existing lazy-create behavior.

**Supported project types**: this question is moot under the interview-based design — there is no metadata-file type detection at all, so the tool behaves identically regardless of project language or ecosystem.

## Consequences

**Positive**: a single atomic tool call brings any project from zero to a fully compliant `.context/` structure; the question registry (`BOOTSTRAP_TARGETS`) is designed to be extended for future bootstrap artifacts without new tool surface; reusing `write_project`/`create_adr` internally means bootstrap inherits their existing local/remote/branch-mode write behavior (and tests) for free; the tool is safe to re-run at any time with no risk of clobbering prior edits.

**Negative / trade-offs**: `project.md` quality depends entirely on the interview answers supplied by the calling agent — there is no automatic fallback content derived from the repository itself, so a bootstrap run with no `project_sections` produces a file that is mostly `[TBD]` placeholders. Remote-provider bootstraps do not produce an empty `sessions/` directory, which could be surprising to a user inspecting the repository tree immediately after bootstrapping. The governance ADR is always titled and scoped identically (ADR-00001, "Consistent Use of..."), so the "skip if any ADR exists" gate is the only protection against creating a duplicate or conflicting ADR-00001 in a project with a different first-ADR convention.

## Alternatives Considered

- **Destructive overwrite of existing files** — rejected. Always overwriting (or overwriting only empty/skeleton-only files) risks silently discarding a user's in-progress edits to `project.md` or the governance docs; the safer additive/skip-existing default was chosen instead.
- **Automatic metadata-file inference** (parsing `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, etc. to pre-fill `project.md`) — rejected in favor of an interactive interview. Metadata files describe dependencies and entry points but not the qualitative content `project.md` needs (architecture rationale, known pain points, active work), and supporting inference would require ongoing maintenance of per-ecosystem parsers.
- **Folding this logic directly into `create_adr` and `write_project`** instead of a dedicated orchestrating tool — rejected. Those tools have single, well-defined responsibilities (write one ADR, write `project.md`); bundling directory creation, governance-doc templating, and multi-artifact idempotency into either of them would overload their contracts. A dedicated `bootstrap_context` orchestrator that delegates to both keeps each tool focused.
