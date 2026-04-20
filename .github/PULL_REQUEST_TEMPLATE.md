## Change Types

<!--
Add one row per distinct type(scope) combination present in this PR's commits.
Type and Scope values are defined in the Commit Message Standards section of CONTRIBUTING.md.
-->

| Type | Scope |
|------|-------|
| `` | `` |

---

## Summary

<!--
A clear explanation of what this PR does and why.
Do not simply restate the title — explain the motivation and the problem being solved.
-->

---

## Changes Made

<!--
A concise bullet-point list of the significant changes introduced.
Include files or modules affected where helpful.
-->

-

---

## Testing

<!--
Describe what was tested and how. Include:
- Which test files were added or modified
- Any edge cases or error conditions covered
- How to reproduce the behavior manually if relevant
-->

-

---

## ADRs Referenced

<!--
List any ADRs that informed, constrain, or are affected by this change.
If a new ADR was created, link to it here.
If none apply, write: None.
-->

-

---

## Checklist

- [ ] All tests pass locally: `pytest tests/`
- [ ] Coverage has not dropped below 100%: `pytest --cov=src/mcp_project_context_server tests/`
- [ ] All linters pass with zero errors: `black --check src/ && isort --check-only src/ && flake8 src/ && mypy src/`
- [ ] Any new or changed public APIs have type annotations and docstrings
- [ ] Any architectural change is covered by a new or updated ADR
- [ ] Branch is up to date with `main`

