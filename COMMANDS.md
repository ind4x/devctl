# devctl Commands Reference

This document provides a comprehensive list of all commands available in the `devctl` CLI.

## Overview

`devctl` is organized into logical command groups. You can always run `devctl --help` or `devctl [command] --help` to get immediate assistance.

---

## 1. Project Initialization (`devctl init`)

Initialize a new project with a standard boilerplate and optimized configuration.

| Command | Usage | Description |
| :--- | :--- | :--- |
| **Spring Boot** | `devctl init spring [name]` | Downloads a Spring Boot project from start.spring.io. |
| **Angular** | `devctl init angular [name]` | Scaffolds a new Angular project. |
| **Vue.js** | `devctl init vue [name]` | Scaffolds a new Vue 3 project via Vite. |
| **NestJS** | `devctl init nest [name]` | Scaffolds a new NestJS backend. |
| **NodeJS** | `devctl init nodejs [name]` | Scaffolds a clean Express + TypeScript project. |
| **ReactJS** | `devctl init react [name]` | Scaffolds a new React project via Vite. |
| **NextJS** | `devctl init nextjs [name]` | Scaffolds a new NextJS project with App Router. |
| **FastAPI** | `devctl init fastapi [name]` | Scaffolds a new FastAPI (Python) project. |
| **Django** | `devctl init django [name]` | Scaffolds a new Django REST Framework project. |
| **Svelte** | `devctl init svelte [name]` | Scaffolds a new SvelteKit project. |
| **Go** | `devctl init go [name]` | Scaffolds a new Go (Fiber) project. |

### Options
*   `--db [postgres|mysql|mongodb]`: Specify the database driver for Spring Boot projects (Default: `postgres`).
*   `--port [number]`: Specify a custom local port for the project.

---

## 2. Resource Scaffolding (`devctl add`)

Inject business resources (Entities, Controllers, Services) into your existing project layers.

| Command | Usage | Description |
| :--- | :--- | :--- |
| **Resource** | `devctl add resource [Name]` | Generates a full-stack feature for the given name. |

### Parameters
*   `--fields, -f`: Define fields in `name:type` format.
    *   Example: `devctl add resource Product -f "name:string,price:double"`
    *   Supported types: `string`, `int`, `double`, `float`, `boolean`, `date`.

---

## 3. Local Orchestration (`devctl run`)

Launch your entire development environment in a single terminal.

| Command | Usage | Description |
| :--- | :--- | :--- |
| **Run** | `devctl run` | Scans for databases, backends, and frontends and runs them. |

### Execution Logic
1.  **Databases**: Starts Docker Compose DB services (from `docker-compose-db.yml`) first and waits for initialization.
2.  **Backends**: Launches Spring, Nest, Express, Python, or Go APIs in parallel.
3.  **Frontends**: Launches Angular, Vue, React, Svelte, or NextJS dev servers.
4.  **Logging**: All output is prefixed by service name and color-coded.

---

## 4. Containerization (`devctl dockerize`)

Generate optimized Dockerfiles for all detected projects.

| Command | Usage | Description |
| :--- | :--- | :--- |
| **Dockerize** | `devctl dockerize [path]` | Scaffolds Multi-stage Dockerfiles for all services. |

### Options
*   `--force`: Overwrite existing Dockerfiles.
*   `--dry-run`: Preview actions without writing files.

---

## 5. Deployment Preparation (`devctl deploy`)

Prepare for multi-service production or staging deployments.

| Command | Usage | Description |
| :--- | :--- | :--- |
| **Deploy** | `devctl deploy [path]` | Generates a global `docker-compose-prod.yml` for all services. |

### Features
*   **Automatic Linking**: Detects database configurations from backends and automatically links them to database services in the global compose file.
*   **Context Aware**: Uses relative paths for builds to ensure the compose file is portable.

---

## 6. Interactive Dashboard (`devctl tui`)

Launch the interactive dashboard to manage local microservices, track system metrics, and view service logs in real time.

| Command | Usage | Description |
| :--- | :--- | :--- |
| **Interactive TUI** | `devctl tui` | Launches the multi-tab interactive developer dashboard. |

### Options
*   `--single` / `-s`: Launches a dense, single-panel console viewport displaying system monitors, active services lists, and logs simultaneously on one screen.

### Navigation Keybindings
*   `Left Arrow / Right Arrow`: Cycle page views.
*   `q`: Quit the application.

---

## 7. Utilities

| Command | Usage | Description |
| :--- | :--- | :--- |
| **Ping** | `devctl ping` | Returns "pong" to verify the CLI is operational. |
| **Help** | `devctl --help` | Displays the global or command-specific help menu. |
