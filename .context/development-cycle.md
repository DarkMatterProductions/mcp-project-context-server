# Claude Code — Project Instructions

## Session Initialization — Mandatory First Step

At the start of every session, before doing anything else:

1. Call `search_context_index` with a broad query (e.g. a project overview
   query) to find `project.md` and any other broadly-relevant files.
2. Call `find_latest_session_file` to get the path of the most recent session
   summary.
3. Call `load_context_files` with `project.md` plus the latest session path
   from step 2.

Do **not** load every ADR or every session file by default — that defeats the
purpose of targeted loading. Only call `search_adr_index` / `search_session_files`
(followed by `load_context_files` with the paths they return) when a specific
task actually requires a past decision or past session's content.

---

## Development Cycle — Mandatory Governance Protocol

Every development request, regardless of size or apparent simplicity, must
follow this cycle exactly. There are no exceptions.

---

### The Cycle

```
Create/Update Plan
      ↓
Generate Proposal
      ↓
Communicate Proposal
      ↓
    ┌─────────────────────────────────────────┐
    │  Was EXPLICIT approval given?           │
    │  NO  → return to Create/Update Plan     │
    │  YES → proceed to Implementation        │
    └─────────────────────────────────────────┘
      ↓
Implementation
```

---

### Phase 1 — Create/Update Plan

Before any proposal is written:

1. Read and understand all files relevant to the request.
2. Identify every system, file, and dependency that will be affected.
3. Identify all unknowns and edge cases.
4. Identify whether more than one valid solution approach exists.
5. Document the plan internally before proceeding.

If new information is received at any later phase that changes the
understanding of the problem, return to this phase and restart.

---

### Phase 2 — Generate Proposal

For every viable solution approach identified in Phase 1:

1. Document what changes, in which files, and why.
2. Document the trade-offs, risks, and limitations of each approach.
3. Identify a recommended approach with explicit reasoning.

If only one approach exists, document it fully and state why no
alternatives are available.

**Multiple options must always be presented when more than one technically
valid approach exists.** Presenting a single option as the only path, when
alternatives exist, is a process violation.

---

### Phase 3 — Communicate Proposal

Present the following to the user in a single, complete response:

1. **Summary** — a brief statement of what problem is being solved.
2. **Options** — all approaches from Phase 2, each with:
    - What it does
    - Trade-offs and risks
    - Why it is or is not recommended
3. **Recommendation** — a single preferred option with explicit reasoning.
4. **Explicit approval request** — end with a clear question asking the
   user to confirm before any implementation begins.

---

### Approval Gate — Hard Stop

**Implementation must not begin until explicit approval is received.**

The following constitute explicit approval:
- "Yes", "Go ahead", "Approved", "Do it", "Proceed", "Implement it"
- Selection of a specific option combined with a directive to proceed
- Any unambiguous instruction to begin implementation

The following do NOT constitute explicit approval:
- Asking a follow-up question
- Providing additional information or clarifying context
- Saying "that sounds good" or "that makes sense" without a proceed directive
- Selecting an option without directing implementation to begin
- Silence or absence of response
- Partial acknowledgement of only some items in a multi-item proposal

If approval is ambiguous, ask for clarification. Do not interpret ambiguity
as approval.

If the user approves only a subset of a multi-item proposal, implement only
the approved items. Return to Phase 1 for unapproved items.

---

### Phase 4 — Implementation

Begin only after explicit approval is confirmed.

1. Implement exactly what was approved — no more, no less.
2. If implementation reveals a scope change or unplanned requirement, stop.
   Return to Phase 1 for the new item. Do not implement it silently.
3. Notify the user if anything discovered during implementation
   contradicts the approved proposal before proceeding.

---

### Scope and Applicability

This cycle applies to:
- New features
- Bug fixes
- Refactors
- Configuration changes
- Infrastructure changes
- Any modification to existing behaviour

This cycle does not apply to:
- Reading files for research or understanding
- Running tests or diagnostic commands
- Reporting findings with no associated change

---

### Violations

Skipping or compressing any phase is a process violation. The most
common violations are:

| Violation | Description |
|---|---|
| Direct implementation | Receiving a request and implementing without a proposal |
| Single-option proposal | Presenting one approach when alternatives exist |
| Ambiguous approval | Treating a non-explicit response as permission to proceed |
| Silent scope expansion | Implementing more than what was approved |
| Restarting without notice | Changing approach mid-implementation without communicating |
