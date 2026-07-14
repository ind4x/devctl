# Changelog

This document tracks all notable changes to the `devctl` project. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
