# devctl

`devctl` is a professional command-line interface (CLI) designed to automate and
orchestrate the development lifecycle for modern full-stack architectures. It
provides a unified workflow for managing backends (Spring Boot, NestJS, Go,
FastAPI), frontends (Angular, Vue, React, NextJS, Svelte), and their
containerization across Linux, macOS, and Windows.

## Core Features

-   **Cross-Platform Architecture**: Out-of-the-box support for Windows, Linux, and macOS utilizing a robust platform abstraction layer.
-   **Multi-Stack Orchestration**: Launch databases, multiple microservices, and
    frontend dev servers with a single command. Includes real-time, prefixed log
    streaming.
-   **Full-Stack Scaffolding**: Generate consistent business resources
    (Entities, DTOs, Controllers, Services) across both backend and frontend
    layers simultaneously.
-   **Instant Infrastructure**: Automatically generate optimized, multi-stage
    `Dockerfiles` and global `docker-compose-prod.yml` configurations by scanning
    your project tree.
-   **Security by Default**: Inject standardized JWT authentication and security
    configurations into new projects.

## Installation

You can install `devctl` locally for development:

```bash
git clone https://github.com/yss-ef/devctl.git
cd devctl
pip install -e .
```

## Quick Start

### 1. Initialize a Full-Stack Project

Create a new backend and frontend in seconds:

```bash
mkdir my-app && cd my-app
devctl init spring api --db postgres
devctl init angular front
```

### 2. Add a Business Resource

Generate a complete vertical slice of your application:

```bash
devctl add resource Product -f "name:string,price:double,quantity:int"
```

### 3. Run the Environment

Launch everything in parallel with automatic database startup:

```bash
devctl run
```

## Supported Stacks

| Type | Frameworks / Technologies |
| :--- | :--- |
| **Backends** | Spring Boot, NestJS, Express (NodeJS), FastAPI, Django, Go (Fiber) |
| **Frontends** | Angular, Vue.js, ReactJS, NextJS, Svelte |
| **Databases** | PostgreSQL, MySQL, MongoDB |

## Documentation

For a detailed reference of all available commands and their options, see the
[Commands Reference](COMMANDS.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
development setup and code quality guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.

---
Authored by Youssef Fellah.
Professional Development Orchestrator.
