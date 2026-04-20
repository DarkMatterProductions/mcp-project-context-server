# Contributing to MCP Project Context Server

Thank you for your interest in contributing to **MCP Project Context Server**! This document outlines the standards and processes that all contributors are expected to follow. Taking the time to read it before submitting changes will make the review process faster and smoother for everyone.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Commit Message Standards](#commit-message-standards)
- [Unit Testing Requirements](#unit-testing-requirements)
- [Linting and Code Style](#linting-and-code-style)
- [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
- [Pull Request Guidelines](#pull-request-guidelines)
- [PR Template](#pr-template)
- [Review Process](#review-process)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

All contributors are expected to behave professionally and respectfully. Harassment, discrimination, or abusive behavior of any kind will not be tolerated. By participating in this project you agree to uphold these expectations in all interactions — issues, pull requests, code reviews, and discussions alike.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/mcp-project-context-server.git
   cd mcp-project-context-server
   ```
3. **Add the upstream remote** so you can stay in sync:
   ```bash
   git remote add upstream https://github.com/DarkMatterProductions/mcp-project-context-server.git
   ```

---

## Development Environment Setup

### Prerequisites

- **Python 3.11+**
- **Ollama** running locally with an embedding model (e.g., `nomic-embed-text`)
- **ChromaDB** (installed automatically as a dependency)

### Install with Development Dependencies

```bash
pip install -e .
pip install testsuite
```

### Verify Your Setup

```bash
# Run the test suite
pytest tests/

# Check linting
flake8 src/
black --check src/
isort --check-only src/
mypy src/
```

---

## Branching Strategy

- **`main`** — stable, releasable code only. Direct pushes are not permitted.
- **Feature branches** — branch off `main` using a descriptive name:
  - `feature/<short-description>` — new functionality
  - `fix/<short-description>` — bug fixes
  - `docs/<short-description>` — documentation-only changes
  - `adr/<ADR-XXXXX-topic>` — ADR additions or updates
  - `chore/<short-description>` — maintenance tasks (dependency updates, CI, etc.)

Always keep your branch up to date with `main` before opening a PR:

```bash
git fetch upstream
git rebase upstream/main
```

---

## Making Changes

Before writing any code, consider whether your change:

- Affects more than one component or module
- Introduces a new integration or dependency
- Reverses or contradicts an existing architectural decision
- Has non-obvious trade-offs or could be misunderstood later

If any of these apply, an ADR may be required. See [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs).

---

## Commit Message Standards

Every commit must include a **clear, detailed message** that explains both *what* changed and *why*. Vague messages like `"fix bug"` or `"update code"` will not be accepted.

### Format

```
<type>(<scope>): <short summary — imperative mood, max 72 chars>

<body — itemized list explaining the motivation, context, and any relevant detail>

<footer — optional: issue references, ADR references, breaking change notices>
```

### Best Practices

#### Subject Line (First Line)
- Use the **`<type>(<scope>):`** prefix from the types table below
- Write in **imperative mood** — *"add feature"* not *"added feature"*
- Keep it **≤ 72 characters**
- Be specific — avoid vague summaries like `"fix bug"` or `"update code"`

#### Body
- Separate from the subject line with a **blank line**
- Use an **itemized list** to explain:
  - **What** changed
  - **Why** it changed (motivation)
  - Any relevant **context or trade-offs**
- Do not simply restate the subject — explain the *reasoning*

#### Footer
- Reference closed issues: `Closes #42`
- Reference relevant ADRs: `ADR-00001`
- Note breaking changes if applicable

### Types

| Type        | When to use                                         |
|-------------|-----------------------------------------------------|
| `breaking`  | A backwards incompatible change to the API or Tools |
| `rewrite`   | Complete rewrites / architectural overhauls         |
| `milestone` | Significant feature milestones / stable releases    |
| `deprecate` | Major deprecation cleanups                          |
| `eos`       | End of support for a runtime/platform               |
| `license`   | License changes                                     |
| `security`  | Security-mandated incompatible changes              |
| `feat`      | A new feature or capability                         |
| `fix`       | A bug fix                                           |
| `test`      | Adding or updating tests                            |
| `docs`      | Documentation changes only                          |
| `refactor`  | Code restructuring with no behaviour change         |
| `chore`     | Build system, tooling, or dependency changes        |
| `adr`       | Adding or updating an Architecture Decision Record  |

### Examples

```
feat(search): add n_results parameter to search_project_context

- The tool previously returned a hardcoded limit of 5 results with no
  way for callers to control the result count
- Exposes n_results as a configurable parameter so callers can tune
  result volume to their use case
- Defaults to 5 to preserve full backward compatibility

Closes #42
Related ADR(s): ADR-XXXXXX
```

```
fix(indexer): handle empty .context/decisions directory gracefully

- The indexer raised a FileNotFoundError when the decisions directory
  existed but contained no .md files
- Added an early return with an informational log message to handle
  this edge case cleanly
- No behaviour change for non-empty directories

Closes #57
```

---

## Unit Testing Requirements

All code changes **must** be accompanied by unit tests. Pull requests that modify logic without corresponding test coverage will not be merged.

### Standards

- **Tests for application source code** live in the `tests/` directory and follow the naming convention `test_<module_name>.py`.
- **Tests for scripts under `.github/tools/`** live **alongside the script** in `.github/tools/`, following the same `test_<script_name>.py` naming convention. Each tools subdirectory maintains its own `conftest.py` for path configuration. Do **not** place tooling script tests in `tests/`.
- **Async functions** must use `pytest-asyncio` and be decorated with `@pytest.mark.asyncio` (or rely on `asyncio_mode = "auto"` in `pyproject.toml`).
- **External dependencies** (ChromaDB, Ollama, filesystem I/O) **must be mocked** in unit tests using `pytest-mock`. Unit tests should never require a running external service.
- **New tools or helper functions** require tests for:
  - The happy path
  - Relevant error/edge cases (empty input, missing files, service unavailability, etc.)

### Coverage Requirement

The project targets **≥ 100% line and branch coverage**. Ensure your changes do not reduce coverage below this threshold. Check coverage locally before submitting:

```bash
pytest --cov=src/mcp_project_context_server --cov-report=term-missing tests/
```

### Running the Full Test Suite

```bash
# Application source tests
pytest tests/

# CI/tooling script tests
pytest .github/tools/

# All tests
pytest tests/ .github/tools/

# With coverage report (application source)
pytest --cov=src/mcp_project_context_server tests/

# A specific test file
pytest tests/test_tool_search_context.py -v
pytest .github/tools/test_build_and_publish.py -v
```

---

## Linting and Code Style

All code must conform to the linting and formatting rules configured in `pyproject.toml`. CI will enforce these checks — fix all issues locally before pushing.

### Tools in Use

| Tool     | Purpose                    | Configuration                       |
|----------|----------------------------|-------------------------------------|
| `flake8` | Style and error checking   | `[tool.flake8]` in `pyproject.toml` |
| `black`  | Opinionated code formatter | `[tool.black]` in `pyproject.toml`  |
| `isort`  | Import ordering            | `[tool.isort]` in `pyproject.toml`  |
| `mypy`   | Static type checking       | `[tool.mypy]` in `pyproject.toml`   |

### Key Rules

- **Line length:** `black` is configured to `240` characters; `flake8` enforces `120` characters for non-formatted sections. Do not introduce lines that violate the `flake8` maximum.
- **Import ordering:** `isort` is configured with `profile = "black"`. Run `isort src/` before committing.
- **Type annotations:** All new public functions and methods must include type annotations. `mypy` is run in CI with `ignore_missing_imports = true`.
- **Docstrings:** Public modules, classes, and functions should have docstrings. Note that several docstring warnings (D100, D104, D105, etc.) are suppressed — see `[tool.flake8]` for the full ignore list.

### Running the Linters

```bash
# Check formatting (non-destructive)
black --check src/
isort --check-only src/
flake8 src/
mypy src/

# Auto-fix formatting
black src/
isort src/
```

All four checks must pass with zero errors before a PR will be reviewed.

---

## Architecture Decision Records (ADRs)

This project uses **Architecture Decision Records** to document significant design decisions. All contributors must understand and honor the ADRs stored in `.context/decisions/`. The full process is described in [`.context/adr-creation-and-review-process.md`](.context/adr-creation-and-review-process.md).

### When an ADR Is Required

Create a new ADR before — not after — implementing any change that:

- Affects more than one component or service
- Introduces or replaces a dependency, integration, or storage backend
- Changes a behavior that was the subject of a previous ADR
- Has non-obvious trade-offs or could be costly to reverse
- Reflects a constraint, policy, or organizational requirement

If you are uncertain whether your change warrants an ADR, open an issue and ask. When in doubt, write the ADR.

### Honoring Existing ADRs

Before writing code, review the relevant ADRs in `.context/decisions/`. Contributions must not:

- Contradict or circumvent an `Accepted` or `Implemented` ADR without first superseding it through the formal ADR process.
- Re-litigate a settled decision in a PR without opening a new ADR.

If you believe an existing decision should be revisited, create a new `Proposed` ADR referencing the original, and initiate the review process described in `.context/adr-creation-and-review-process.md`.

### ADR File Conventions

- **Location:** `.context/decisions/`
- **Naming:** `ADR-XXXXX-<kebab-case-topic>.md` (zero-padded 5-digit number)
- **Template:** Use the exact template defined in `.context/adr-creation-and-review-process.md`. Do not add or remove sections.
- **Never delete** an ADR file, even if it is deprecated or superseded.

### Commit Convention for ADRs

```
adr(ADR-XXXXX): accept decision on <topic>
```

---

## Pull Request Guidelines

### Before Opening a PR

Ensure the following are true:

- [ ] All tests pass locally: `pytest tests/`
- [ ] Coverage has not dropped below 100%: `pytest --cov=src/mcp_project_context_server tests/`
- [ ] All linters pass with zero errors: `black --check src/ && isort --check-only src/ && flake8 src/ && mypy src/`
- [ ] Any new or changed public APIs have type annotations and docstrings
- [ ] Any architectural change is covered by a new or updated ADR
- [ ] Your branch is up to date with `main`

### PR Title

Write the title in **imperative mood** as a plain summary of the change — ≤ 72 characters. Do **not** use a `<type>(<scope>):` prefix in the title. Type and scope information belongs in the **Change Types** table in the PR description (see below), because a single PR may span multiple commit types and a single-type prefix would lose that signal.

**Good:** `Add semantic versioning and release automation script`
**Bad:** `chore(ci): add semantic versioning and release automation script`

### PR Description

Every PR **must** include a thorough description using the template at `.github/PULL_REQUEST_TEMPLATE.md`. The following sections are required:

#### Change Types
A table mapping each `type` and `scope` present in the PR's commits to a short description of what that group of changes covers. This replaces the single-type prefix that would appear in a commit subject line.

```markdown
## Change Types

| Type | Scope |
|------|-------|
| `chore` | `ci` |
| `docs` | `claude` |
```

Every distinct `type(scope)` combination in the PR's commits must appear as a row. Use the type values defined in the [Commit Message Standards](#commit-message-standards) types table.

#### Summary
A clear explanation of what this PR does and why. Do not simply restate the title. Explain the motivation and the problem being solved.

#### Changes Made
A concise bullet-point list of the significant changes introduced. Include files or modules affected where helpful.

#### Testing
Describe what was tested and how. Include:
- Which test files were added or modified
- Any edge cases or error conditions covered
- How to reproduce the behavior manually if relevant

#### ADRs Referenced
List any ADRs that informed, constrain, or are affected by this change. If a new ADR was created, link to it here.

#### Checklist
Include the pre-PR checklist above in your description and check off each item.

### PR Template

A GitHub PR template is provided at `.github/PULL_REQUEST_TEMPLATE.md`. It pre-populates the required sections when you open a new PR. Fill in every section — do not delete any headings.

---

## Review Process

1. **Automated checks** (linting, tests, coverage) run on every PR via CI. All checks must pass before a human review is requested.
2. **A maintainer** will review the code for correctness, test coverage, adherence to linting rules, and compliance with ADRs.
3. **Feedback** will be given via inline comments or a review summary. Address all comments before re-requesting review.
4. **Approval and merge** — once approved, a maintainer will merge the PR using squash-merge to keep the `main` history clean.

---

## Reporting Issues

If you have found a bug or have a feature request:

1. **Search existing issues** first — it may already be reported.
2. **Open a new issue** using the appropriate template (bug report or feature request).
3. Include as much context as possible: Python version, OS, environment variables (redacted), steps to reproduce, and expected vs. actual behavior.

For security vulnerabilities, **do not open a public issue**. Contact the maintainers directly at [pypi@darkmatter-productions.com](mailto:pypi@darkmatter-productions.com).

---

## Questions?

If you have questions about the contribution process or the project architecture, open a [GitHub Discussion](https://github.com/DarkMatterProductions/mcp-project-context-server/discussions) or reach out via the Issues tracker.

---

<div align="center">

**Thank you for contributing to MCP Project Context Server.**

</div>

