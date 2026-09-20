# ADR-00026: Structured diagnostics for empty/filtered search results

## Status
Proposed

## Context

`search_context_index`, `search_adr_index`, `search_session_files`, and `search_adr_sections` all funnel through one shared function, `run_search()` in `src/mcp_project_context_server/tools/search_shared.py`. That function already distinguishes several failure modes with specific messages: no `.context/` directory found, collection not yet indexed, and embedding/vector-store call failures. But it collapses two very different "nothing to show" situations into a single generic branch:

```python
if not documents:
    return _empty_result(f"{warning_prefix}No results found.")
```

This fires identically whether:

1. The unscoped top-K vector query genuinely found nothing semantically close anywhere in the collection, or
2. For the *scoped* tools (`search_adr_index`, `search_session_files`, `search_adr_sections` — which pass `file_prefix` or `exact_file`), the top-K query returned real hits, but the post-hoc prefix/exact-file filter removed every one of them because they all belonged to other files in the collection.

Case 2 is a distinct, more specific failure than case 1: the caller's query wasn't necessarily "bad" — it just didn't surface a hit within the *scope* it asked for, and the caller has no way to tell whether that's because (a) nothing relevant exists in that scope at all, or (b) relevant content exists in that scope but ranked below the over-fetch cutoff (`_OVER_FETCH_FLOOR` / `_OVER_FETCH_MULTIPLIER`, currently 25 / ×5) applied before filtering.

This was surfaced concretely during an ADR-status audit of this project: `search_adr_index(query="Proposed status architecture decision record")` returned `{"results": []}` with the text "No results found." The caller (an LLM agent) could not tell from that response whether the ADR index had no relevant content at all, or whether the query's nearest neighbors in the wider collection simply weren't tagged under `decisions/`. It had to abandon the tool and fall back to exhaustive `Glob`/`Grep` over every ADR file to get a reliable answer — exactly the kind of tool-abandonment this server's granular ADR tools (ADR-00012) were built to avoid.

Three sub-decisions need resolving:

**Sub-decision 1 — What diagnostic information to compute.** At minimum: whether the empty result came from the unfiltered query or from the prefix/exact-file filter removing all candidates (`search_shared.py:149-168`). Optionally: the count of candidates fetched before filtering, the count remaining after filtering (always 0 in the empty case, but useful as a sanity signal if this is reused for a "few but not enough" case later), and the best (lowest) distance seen among the discarded candidates, so a caller can judge "close but out of scope" versus "nothing related at all."

**Sub-decision 2 — Where to expose it.** Options:
- Text only: fold the diagnostic into the human-readable message (e.g., "Found 12 matches in the wider index, but none were under `decisions/`. Try `search_context_index` to search unscoped, or increase `n_results`.").
- Structured only: add fields to `structured_content` (e.g., `{"results": [], "reason": "filtered_to_empty", "candidates_before_filter": 12}`) without changing the text.
- Both: the text carries an actionable, human-readable suggestion; `structured_content` carries the same information as machine-checkable fields so a calling agent can branch on `reason` without parsing prose.

**Sub-decision 3 — Scope of the fix.** Options:
- Fix only the filtered-to-empty case (case 2 above), since it's the one with an unambiguous root cause today.
- Also enrich the unfiltered-empty case (case 1) with a best-distance signal, which requires no filtering logic change but does require carrying the pre-filter query result's distances into the empty-result path even when `documents` end up empty.

## ADR Review Discussion
[Discussion pending]

## Decision
[Pending review]

## Consequences

- All four search tools (`search_context_index`, `search_adr_index`, `search_session_files`, `search_adr_sections`) inherit the fix for free, since they share `run_search()` — no per-tool changes needed.
- Calling agents get an actionable next step instead of a dead end, reducing the chance they abandon the semantic-search tools for exhaustive file scanning (as happened in the incident that prompted this ADR).
- `structured_content` gains new optional fields (e.g. `reason`, `candidates_before_filter`) on the empty-result path; this is additive and should not break existing callers that only read `results`.
- Slightly more bookkeeping in `run_search()`: the pre-filter candidate count and best distance must be retained even when the post-filter set is empty, whereas today they are discarded as soon as filtering happens.
- No changes to indexing, chunking, or the vector store itself — this is purely a response-shaping change at the tool layer.

## Alternatives Considered

- **Increase `_OVER_FETCH_FLOOR`/`_OVER_FETCH_MULTIPLIER` instead of adding diagnostics**: would reduce how often case 2 happens but can't eliminate it (any fixed over-fetch window can still miss a relevant chunk ranked further down), and does nothing to explain the *other* empty case (case 1) or any future occurrence. Treats the symptom, not the caller's inability to distinguish causes.
- **Leave the message generic but always suggest `search_context_index` as a fallback**: cheap, but gives the same advice regardless of whether it would actually help — misleading when the true cause is "nothing relevant exists anywhere," not "wrong scope."
- **Do nothing; rely on callers to fall back to `list_*`/`Glob`/`Grep` tools when semantic search comes up empty**: this is what already happens today (as in the incident above) and defeats the purpose of having scoped semantic-search tools at all for exactly the queries they're least confident about.
