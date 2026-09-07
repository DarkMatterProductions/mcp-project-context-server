# ADR-00025: AST-based filter expressions for list_adrs

## Status
Proposed

## Context
Today's `list_adrs` returns every ADR in `.context/decisions/` with no way to narrow the result set. As the number of ADRs grows, callers (human or LLM) need to filter by structural fields before scanning the full list.

Looking at `.context/decisions/` (24 files today) and the parsing logic in `helpers/adr.py`, the fields that can be reliably parsed for every ADR regardless of header style are: a numeric identifier (from the filename), `title`, `status` (the raw first line under `## Status`, which is empty for the 7 files still using the legacy `**Status:**` inline style), and `malformed` (set when title/status parsing fails). `**Date:**` and `**Author:**` exist on only 7 of the 24 files with no parser for them today, so date/author filtering is out of scope for this change — supporting it now would silently exclude most existing ADRs and would duplicate the dual-format parsing work already flagged as deferred in ADR-00012.

Two shapes for the filtering API were weighed:

- **(A) Declarative per-dimension parameters** — e.g. `status=`, `title_contains=`, `number_min=`/`number_max=`, `malformed_only=`. Simple to call, but does not compose: expressing an OR or a compound condition across dimensions requires new parameters each time, and the parameter set is specific to `AdrInfo` — it isn't reusable by any other "list"-style tool this project might add later.
- **(B) A single filter-expression string** parsed with `ast.parse(expr, mode="eval")` and evaluated by walking the resulting tree against a narrow whitelist: `BoolOp` (`and`/`or`), `UnaryOp` (`not`), `Compare` (`==`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `not in`), bare `Name` nodes restricted to a caller-supplied allow-list of field names, and literal `Constant` values (str/int/float/bool/None). Any other node type — calls, attribute access, subscripts, comprehensions, lambdas — is rejected before evaluation, so this is never a raw `eval()`/`exec()` on untrusted input.

Option (B) was chosen. Because the evaluator only needs a field-name-to-value mapping and an allow-list to do its job, it doesn't belong in `helpers/adr.py` — it belongs in a new, document-agnostic helper module that any current or future "list" tool can adopt by supplying its own small field-mapping function and allow-list, with no changes to the evaluator itself.

This decision also settles a naming question that reaches beyond `list_adrs`: the existing `AdrInfo.number` field is renamed to `AdrInfo.id` everywhere it appears (not just in the new filter vocabulary), so the codebase has a single name for the concept. `number` is specific to ADRs; `id` is the generic term that other future filterable document types would also use through the same shared evaluator.

## ADR Review Discussion
[Discussion pending]

## Decision
[Pending review]

## Consequences

- New reusable primitive: a generic safe filter-expression evaluator (e.g. `helpers/filter_expr.py`) that any current or future "list" tool can adopt by supplying its own field-mapping function and allow-list — no evaluator changes needed to add a new document type's filterable fields.
- `list_adrs` trades fixed dimensions for one `filter` string parameter over `id`/`title`/`status`/`malformed` with `and`/`or`/`not` and comparison operators — strictly more expressive (supports OR/compound conditions) at the cost of agents constructing a small expression instead of passing named arguments.
- `AdrInfo.number` -> `AdrInfo.id` rename ripples into `helpers/adr.py` (`list_adrs`, `resolve_adr`, `_match_adr`), all five existing ADR tool handlers that build `ADR-{...:05d}` output or accept a numeric `number_or_filename`, and every test in `test_helpers_adr.py`, `test_tool_list_adrs.py`, and the four sibling tool test files that asserts on `.number` — mechanical but wide-reaching, outside the filtering feature itself.
- The filter string is untrusted LLM/remote-caller input (ADR-00017 allows HTTP/SSE exposure) — the evaluator must reject unknown fields/disallowed constructs outright and bound expression length/AST depth against pathological input.
- Raw `status` stays messy (e.g. `"Superseded by ADR-00012"`, `"Implemented (drop-and-recreate on manual trigger)"`); this ADR keeps `status` as the raw string per the requested four-field scope rather than adding a normalized-category derived field — noted as a candidate follow-up, not resolved here.
- Additive per ADR-00004: one new helper module plus changes to the single existing `list_adrs` tool; no new tool files.

## Alternatives Considered

- **Declarative per-dimension parameters**: rejected as the primary design — doesn't compose (no OR/compound conditions without adding new parameters each time) and the parameter set is `AdrInfo`-specific, not reusable by other tools.
- **`eval()`/`exec()` on the raw string**: rejected outright — arbitrary code execution risk from LLM- or remote-supplied input.
- **A third-party expression/query library** (e.g. `simpleeval`): rejected to avoid a new dependency when the standard-library `ast` module covers this narrow need with an explicit, auditable node-type whitelist.
- **A normalized `status_category` derived field**: deferred — the four requested fields are sufficient to start; status-text normalization is orthogonal cleanup already flagged as unresolved in ADR-00012.
- **Keep `AdrInfo.number`, expose `id` only as a filter-vocabulary alias**: rejected per explicit direction — two names for one concept in the codebase was judged worse than a one-time mechanical rename.
