# ADR-00011: Repository bootstrapping tool

## Status
Proposed

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

## ADR Review Discussion

1. **Destructive vs. additive behavior**: Should `bootstrap_context` overwrite existing files, or skip files that already exist? An additive approach (skip existing) is safer — it prevents clobbering a hand-crafted `project.md`. A destructive approach (overwrite) ensures the template is always current. A middle ground: overwrite only if the file is empty or contains only the template skeleton (no user-added content).

2. **Content inference depth**: How much should the tool infer from project metadata files? At minimum: project name and one-liner from `pyproject.toml` (name, description) or `package.json` (name, description). At maximum: full tech stack, dependencies, entry points, and architecture notes derived from the full project structure. The right scope for a bootstrap is "enough to be useful, not so much that it's wrong" — the agent or user refines from there.

3. **Fallback when no metadata file is found**: If none of `pyproject.toml`, `package.json`, `README.md`, `go.mod`, or `Cargo.toml` are present in the project root, the tool should still create the skeleton — with placeholder text in each `project.md` section rather than leaving the file empty or failing.

4. **Auto-index after bootstrap**: Should `bootstrap_context` immediately call `index_project_context` after creating the skeleton? This would make the context server immediately queryable with the bootstrapped content. The downside is that a newly-bootstrapped `project.md` is mostly placeholder text — indexing it immediately may not be useful. This could be an opt-in parameter (`auto_index: bool = False`).

5. **Idempotency**: Should calling `bootstrap_context` on a project that already has `.context/` be a no-op, an error, or a partial update? Idempotency (no-op for existing files, create missing ones) is the safest default.

6. **Supported project types**: The initial implementation should handle `pyproject.toml` (Python) and `package.json` (Node.js) as the two most common cases. Additional project types (`go.mod`, `Cargo.toml`, `build.gradle`) can be added incrementally.

## Decision

TBD — pending resolution of the design questions above.

## Consequences

TBD

## Alternatives Considered

TBD — to be populated when the decision is made.
