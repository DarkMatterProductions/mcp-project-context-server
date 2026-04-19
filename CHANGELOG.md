# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

[Unreleased]: https://github.com/DarkMatterProductions/mcp-project-context-server/compare/cca6114...HEAD

