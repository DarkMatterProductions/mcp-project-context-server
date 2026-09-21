# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

### Changed

### Fixed

---

## [1.3.1] - 2026-09-21

### Changed
- Migrate Google embeddings provider from `google-generativeai` to the native-async `google-genai` SDK, updating `pyproject.toml`, `requirements.txt`, and `ADR-00014` accordingly (`a6251d0`)
- Update integration tests to expect 22 registered tools (`get_bootstrap_questions`, `bootstrap_context`) (`2d8eaa7`)
- Consolidate commit-validation and version-bump logic (`analyze_commits`, `determine_bump`, `determine_new_version`, `key_id_lookup`) into shared `.github/tools/shared_helpers.py` and `.github/tools/constants.py`, removing duplication between `validate_commits.py` and `build_and_publish.py` (`7cb58ff`, `1d90102`)

### Fixed
- Add exponential-backoff retry handling to the Voyage AI embedding provider for transient errors (429, 5xx, timeouts), configurable via `VOYAGE_BACKOFF_INITIAL_DELAY` (default 300s, doubling per attempt up to 4 attempts), with `x-request-id` logging and a one-time reduced-tier rate-limit warning (`9427fc8`)
- Centralize commit-validation constants (`COMMIT_TYPES`, `INCREMENT_BUMP_TYPE_MESSAGES`, `RELEASE_OVERRIDE_SCOPES`) into `.github/tools/constants.py`, shared by `validate_commits.py` and `build_and_publish.py` (`5bbcdad`)

---

## [1.2.1]

### Fixed
- Fixed the version assignment in the `CHANGELOG.md` file due to commit validation issues on build and release.

---

## [1.2.0] - 2026-09-20

### Added
- Add ADR-00012 toolset: `list_adrs`, `read_adr`, `read_adr_status`, `list_adr_sections`, `read_adr_section`, `edit_adr`, `search_adr_sections`, `update_adr_status`, and `create_adr` MCP tools, along with `helpers/adr` parsing and resolution utilities (`8f20b86`)
- Add branch-based remote write support for ADR tools via `REPO_ADR_WRITE_MODE` (`branch`/`direct`), including optional auto-reindexing after writes (`8f20b86`)
- Add heading-based markdown splitting utilities (`split_sections`, `chunk_section`) implementing ADR-00007's chunking strategy (`a243b86`)
- Add heading-based chunking to the indexer with `section`/`section_sha512` chunk metadata for cheap per-section change detection (`f7b7713`)
- Add `_MAX_CHUNK_SIZE` environment variable to override the indexer's chunk size (`f7b7713`)
- Add ADR-00025 proposing safe, AST-based filter expressions for `list_adrs`, with a reusable filter evaluator in `helpers/filter_expr.py` (`5f3c83c`)
- Add ADR-00026, ADR-00027, ADR-00028, and ADR-00029 documenting proposed structured-diagnostics, YAML configuration, cloud embedding provider, and watchdog-based auto-reindex features (`c5c5240`)
- Add `repomix.config.json` and `.repomixignore` for repository packaging/documentation bundling (`3bf0413`)
- Add CLAUDE.md instruction to always leverage the `project_context` connector tools (`937448a`)
- Add `bootstrap_context` and `get_bootstrap_questions` MCP tools with a reusable, extensible question registry (`helpers/bootstrap_templates.py`, `helpers/custom_bootstrap_questions.py`) for interview-driven `.context/` scaffolding (`e0ca1e2`)
- Add `ADR_CREATE_AND_MANAGEMENT.md` and `PLANNING_LOOP.md` governance templates, bundled as package data and read via `importlib.resources` (`e0ca1e2`)
- Add `fetch_root_file` implementation across GitHub, GitLab, Gitea, and Local repository providers, with support for merging custom bootstrap questions from a `.project-bootstrap-questions.yaml` file at the repository root (`e0ca1e2`)
- Add `pyyaml>=6.0` dependency for YAML file parsing (`e0ca1e2`)
- Add `validate_commits.py` script and `validate-commits.yml` CI workflow to enforce `type(scope):` commit message conventions on pull requests (`c219b2a`)

### Changed
- Accept ADR-00012, consolidating the ADR/`project.md` tool surface and superseding ADR-00010 (`937448a`)
- Accept ADR-00007, adopting heading-based chunking with intelligent sub-splitting as the official markdown indexing strategy (`43ffa9e`)
- Rename `AdrInfo.number` to `AdrInfo.id` across the codebase for consistency with the new filter-expression tooling (`5f3c83c`)
- Update ADR-00006, ADR-00005, and ADR-00003 statuses to reflect superseding/tracking decisions (ADR-00029, ADR-00028, ADR-00014 respectively) (`c5c5240`)
- Restructure `BUNDLE.md` with proper Markdown headers and expanded directory/file examples (`a789c88`)
- Improve embedding-failure logging in the indexer so partial failures are surfaced instead of silently dropped (`f7b7713`)
- Improve error diagnostics for indexing failures in integration tests (`70a5436`)
- Accept ADR-00011, replacing its open design questions with the implemented interview-driven, additive-only `bootstrap_context` design: content is resolved via `get_bootstrap_questions` answers rather than metadata-file inference, all artifacts are additive-only (skip if already present), and the governance ADR is created via the existing `create_adr` tool (`e0ca1e2`)
- Tighten type annotations and null-safety across ADR utilities and response parsing, including optional `status` handling in `read_adr_status` and broader `repos_content_results` content types (`5a3d4f0`, `6972be4`)
- Restrict the Qodana workflow to run only on `pull_request` targeting `main`, dropping the unused `workflow_dispatch` trigger and `push`/`releases/*` branch triggers (`c219b2a`)

---

## [0.0.4] - 2026-04-17

### Fixed
- Refactor GitHub release creation in `build-and-publish.py` include a missing path to the location of the artifacts to be published. (`184d85e`)

---

## [0.0.3] - 2026-04-17

### Fixed
- Refactor GitHub release creation in `build-and-publish.py` to use `subprocess.Popen` for proper output capture; buffered output is now printed when the release process fails
- Improve error logging in `build-and-publish.py` so that buffered build output is printed when `python -m build` exits with a non-zero return code and `--verbose` is not set (`b423688`)

---

## [0.0.2] - 2026-04-17

### Fixed
- Improve error output in `build-and-publish.py` so that buffered build output is printed when the process exits with a non-zero return code and `--verbose` is not set (`b423688`)

---

## [0.0.1] - 2026-04-17

### Added
- Implement MCP project context server with semantic search via ChromaDB and Ollama embeddings (`41d1888`)
- Add `load_project_context`, `search_context`, `index_context`, and `save_session` MCP tools (`41d1888`)
- Add synchronous and asynchronous Ollama embedding client (`e1fbfc7`)
- Add heading-boundary chunking strategy for markdown indexing with intelligent sub-splitting (`a9f9d81`)
- Add Architecture Decision Records (ADRs) for server protocol, ChromaDB, and Ollama integration (`e5728d6`)
- Add ADR creation and review process documentation (`0bd33ed`)
- Add ADR-00010: GitHub Actions workflow for Codecov coverage uploads (`17713d4`)
- Add ADR-00012 and ADR-00013: targeted ADR/project tools and lightweight session initialization (`2f19a3e`)
- Add `build-and-publish.py` script for semantic versioning and automated GitHub releases (`e02dad0`)
- Add `build-and-publish.yml` GitHub Actions workflow for automated PyPI publishing on tag push (`e02dad0`)
- Add `codecov.yaml` GitHub Actions workflow for automated coverage uploads (`17713d4`)
- Add `.coveragerc.toml` with comprehensive coverage exclusion rules (`e420232`)
- Add `pytest.ini` to configure `pytest-asyncio` for asynchronous testing (`b00c6ca`)
- Add test suites: `test_helpers`, `test_tool_index_context`, `test_tool_load_context`, `test_tool_save_session`, `test_tool_search_context` (`3940347`)
- Add LICENSE (AGPLv3) and comprehensive README with setup instructions for all major MCP clients (`d80997b`, `312eae4`)
- Add README badges for PyPI version, downloads, coverage, last commit, and issues (`32a5c7c`, `6776ad5`)
- Add `CHROMA_DIR` environment variable documentation and server connection verification instructions to README (`60f4c4b`)
- Add dynamic version handling in `__init__.py` via `setuptools_scm` with `_version` fallback (`bd690e2`)
- Add `mypy` to test dependency group for static type checking (`b00c6ca`)

### Changed
- Refactor project namespace from `project_context_server` to `mcp_project_context_server` (`e1fbfc7`)
- Refactor project path handling to use `PROJECT_PATH` environment variable across all tools (`12d94ef`)
- Refactor test cases into class-based structures for improved organisation (`57522ef`)
- Refactor `search_context.py` to use `cast` for query embeddings and improve `None`-safety in result handling (`fc69c02`)
- Consolidate import statements and remove unnecessary whitespace across the codebase for consistency (`5faca4a`)
- Switch build backend from `hatchling` to `setuptools` with `setuptools_scm` for version management (`bd690e2`)
- Update project URLs in `pyproject.toml` to reflect `DarkMatterProductions` organisation branding (`47969a0`)
- Update `tag_regex` in `pyproject.toml` to correctly capture version numbers (`f60ef63`)
- Update CI to use `actions/checkout@v6` and `actions/setup-python@v6` (`3ee6cf2`)
- Update CI dependency installation to use `pip install testsuite` with explicit pip upgrade (`ee6c917`, `2e094b3`)
- Update `pyproject.toml` dependency versions for improved compatibility (`5faca4a`)

### Fixed
- Add specific `subprocess.CalledProcessError` handling in `build-and-publish.py` with detailed error output (`ed64a31`)
- Fix logging configuration in `server.py` to write to a log file instead of stderr (`bac831c`)

### Removed
- Remove legacy monolithic `context_server.py` and misplaced `AGENTS.md` references from project documentation (`caeda77`)
- Remove redundant `pip install -e .` step from CI configuration (`7f7983f`)
- Remove IntelliJ IDEA run configuration from version control (`d3893df`)

---

[Unreleased]: https://github.com/DarkMatterProductions/mcp-project-context-server/compare/1.1.0...HEAD
[1.1.0]: https://github.com/DarkMatterProductions/mcp-project-context-server/compare/cca6114...1.1.0

