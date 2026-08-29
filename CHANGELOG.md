# Changelog

This document tracks all notable changes to the `devctl` project. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.3] - August 29, 2026

### Fixed

- **SvelteKit Generator:** Fixed `sv create` CLI flags (`--template minimal`, `--types ts`, and `--no-add-ons`) for compatibility with Svelte CLI v0.17+.
- **Vite Generators:** Added `--no-interactive` flags to `npm create vite@latest` in React and Vue generators for non-interactive execution.
- **Node.js Generator & Templates:** Fixed `ts-node` type imports in Jinja templates and auto-patched `tsconfig.json` (`verbatimModuleSyntax: false`).
- **TUI Select Component:** Removed fixed height CSS constraints (`height: 1`) on `Select` containers in `app.tcss` and added default initial selections (`value="spring"`).
- **TUI Thread Safety:** Wrapped UI updates in `call_from_thread` within `trigger_rescan_and_refresh` to prevent cross-thread widget state mutations.

## [1.2.2] - August 24, 2026

### Changed

- **Version Bump:** Bumped project version to 1.2.2.

## [1.2.1] - August 24, 2026

### Added

- **Self-contained Framework Packages:** Converted all generators (`angular`, `django`, `docker`, `fastapi`, `go_fiber`, `nestjs`, `nextjs`, `nodejs`, `react`, `spring`, `svelte`, `vue`) into modular, self-contained packages under `devctl/generators/<framework>/`.
- **Standardized Jinja2 Templates:** Replaced all inline Python f-string stubs with standardized Jinja2 `.j2` template files stored locally within each framework's package (`devctl/generators/<framework>/templates/`).
- **Local Package Tests:** Co-located framework-specific unit tests directly within each framework package (`devctl/generators/<framework>/tests/`).
- **Framework Contribution Guide:** Added detailed developer guidelines in `CONTRIBUTING.md` on how to add and structure new framework packages.

### Changed

- **Clean Imports:** Refactored command submodules (`devctl/commands/init.py`, `add.py`, `docker.py`, `deploy.py`, `run.py`) to consume unified framework APIs exposed by `__init__.py`.
- **Packaging:** Updated `pyproject.toml` to automatically include modular Jinja2 templates (`generators/**/templates/**/*.j2`) while excluding local framework tests from wheel builds.

## [1.2.0] - July 17, 2026

### Added

- Interactive CLI TUI: Introduced a comprehensive dashboard for scanning projects, managing processes, and viewing live logs.
- System metrics: Added real-time CPU, RAM, and Disk space tracking progress bars.
- Single-panel layout: Support for a dense, single-viewport dashboard rendering (triggered via `devctl tui --single`).
- Keyboard navigation bar: Added arrow key navigation bar hints to quickly shift between views.
- Test coverage: Expanded coverage with `test_tui.py` for testing widgets, progress indicators, and compose states.

## [1.1.0] - July 14, 2026

### Added

- Cross-platform support: Added full Windows operating system compatibility.
- Platform abstraction layer: Introduced `BasePlatform`, `WindowsPlatform`, and `UnixPlatform` to cleanly encapsulate OS-specific pathing, shell flags, and execution commands.
- Unit testing: Added test coverage for the platform helper module (`test_platform.py`).

### Changed

- Refactored orchestrator runner (`runner.py`) and all framework generators to consume the platform abstraction factory instead of executing platform-specific checks inline.

## [1.0.0] - May 20, 2026

### Added

- Vue.js support: Added Vue 3 TypeScript resource scaffolding, including
  components, models, and services.
- Security and CI: Integrated CodeQL for security scanning, Semantic PR
  linter, and Release Drafter.
- Documentation: Added internal architecture documentation and standardized
  engine documentation headings.
- License: Added MIT License.

### Changed

- Internationalization: Completed translation of CLI messages, comments, and
  docstrings into English.
- Refactoring: Standardized signatures across all documentation and improved
  template organization.
- Cleanup: Removed emojis and refined the tone of all documentation for
  professional standards.

### Fixed

- Security: Resolved CodeQL Jinja2 XSS warnings in Vue scaffolding.
- Reliability: Fixed accidental removal of test files and standardized code
  formatting using Ruff.

## [0.2.0] - April 15, 2026

### Added

- Deployment: Added the `deploy` command to generate unified Docker Compose
  files.
- Dockerization: Added the `docker` command for scaffolding production-ready
  Dockerfiles.
- Scaffolding expansion: Integrated Angular resource creation and enhanced
  Spring resource management.
- Quality tools: Integrated Ruff, Dependabot, and CodeRabbit for automated
  code quality and dependency management.

### Fixed

- Spring integration: Resolved Maven dependency issues and resource generation
  bugs.
- Authentication: Updated the authentication provider for compatibility with
  newer Spring versions.
- Networking: Refactored Spring CORS configuration to support reverse proxy
  architectures.

## [0.1.0] - March 1, 2026

### Added

- Core orchestrator: Initial implementation of the `devctl` CLI with `init` and
  `run` commands.
- Environment detection: Added automatic detection of Spring Boot, Angular,
  and Docker-based databases.
- Spring scaffolding: Implemented base Spring Boot boilerplate generation.
- Local release: Stabilized core features for local environment launch and
  project initialization.
