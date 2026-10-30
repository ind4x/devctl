"""
Agent context generator.
Produces AGENTS.md, CLAUDE.md, and .cursorrules for AI coding assistants.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Union

import typer
import yaml
from jinja2 import Environment, FileSystemLoader

from devctl.generators.docker.scaffolder import IGNORED_DIRECTORIES, discover_docker_projects

FRAMEWORK_METADATA: Dict[str, Dict[str, Any]] = {
    "spring": {
        "framework": "Spring Boot",
        "category": "backend",
        "default_port": 8080,
        "run_cmd": "./mvnw spring-boot:run",
        "test_cmd": "./mvnw test",
    },
    "fastapi": {
        "framework": "FastAPI",
        "category": "backend",
        "default_port": 8000,
        "run_cmd": "uvicorn main:app --reload",
        "test_cmd": "pytest",
    },
    "django": {
        "framework": "Django",
        "category": "backend",
        "default_port": 8000,
        "run_cmd": "python manage.py runserver",
        "test_cmd": "python manage.py test",
    },
    "nest": {
        "framework": "NestJS",
        "category": "backend",
        "default_port": 3000,
        "run_cmd": "npm run start:dev",
        "test_cmd": "npm test",
    },
    "nodejs": {
        "framework": "NodeJS / Express",
        "category": "backend",
        "default_port": 3000,
        "run_cmd": "npm run dev",
        "test_cmd": "npm test",
    },
    "go": {
        "framework": "Go (Fiber)",
        "category": "backend",
        "default_port": 3000,
        "run_cmd": "go run .",
        "test_cmd": "go test ./...",
    },
    "angular": {
        "framework": "Angular",
        "category": "frontend",
        "default_port": 4200,
        "run_cmd": "npx ng serve",
        "test_cmd": "npm test",
    },
    "vue": {
        "framework": "Vue 3",
        "category": "frontend",
        "default_port": 5173,
        "run_cmd": "npm run dev",
        "test_cmd": "npm test",
    },
    "react": {
        "framework": "React",
        "category": "frontend",
        "default_port": 5173,
        "run_cmd": "npm run dev",
        "test_cmd": "npm test",
    },
    "nextjs": {
        "framework": "Next.js",
        "category": "frontend",
        "default_port": 3000,
        "run_cmd": "npm run dev",
        "test_cmd": "npm test",
    },
    "svelte": {
        "framework": "Svelte",
        "category": "frontend",
        "default_port": 5173,
        "run_cmd": "npm run dev",
        "test_cmd": "npm test",
    },
}


def _detect_service_port(project_path: Path, kind: str, default_port: int) -> int:
    """Extract configured service port or fallback to default."""
    if kind == "spring":
        props_path = project_path / "src" / "main" / "resources" / "application.properties"
        if props_path.exists():
            try:
                content = props_path.read_text(encoding="utf-8")
                match = re.search(r"^server\.port\s*=\s*(\d+)", content, re.MULTILINE)
                if match:
                    return int(match.group(1))
            except Exception:
                pass
    return default_port


def _discover_databases(root: Path) -> List[Dict[str, Any]]:
    """Scan for docker-compose-db.yml files and extract service configuration."""
    databases: List[Dict[str, Any]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRECTORIES]
        if "docker-compose-db.yml" in filenames:
            compose_path = Path(dirpath) / "docker-compose-db.yml"
            try:
                content = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
                services = content.get("services", {})
                for s_name, s_conf in services.items():
                    image = str(s_conf.get("image", "unknown"))
                    ports = s_conf.get("ports", [])
                    host_port = "unknown"
                    if ports:
                        raw_port = str(ports[0])
                        host_port = raw_port.split(":")[0] if ":" in raw_port else raw_port

                    env_vars = s_conf.get("environment", {})
                    if isinstance(env_vars, list):
                        parsed_env = {}
                        for item in env_vars:
                            if isinstance(item, str) and "=" in item:
                                k, v = item.split("=", 1)
                                parsed_env[k.strip()] = v.strip()
                        env_vars = parsed_env

                    db_user = (
                        env_vars.get("POSTGRES_USER")
                        or env_vars.get("MYSQL_USER")
                        or env_vars.get("MONGO_INITDB_ROOT_USERNAME")
                        or "admin"
                    )
                    db_password = (
                        env_vars.get("POSTGRES_PASSWORD")
                        or env_vars.get("MYSQL_PASSWORD")
                        or env_vars.get("MONGO_INITDB_ROOT_PASSWORD")
                        or "password"
                    )
                    db_name = (
                        env_vars.get("POSTGRES_DB")
                        or env_vars.get("MYSQL_DATABASE")
                        or env_vars.get("MONGO_INITDB_DATABASE")
                        or "default_db"
                    )

                    image_lower = image.lower()
                    if "postgres" in image_lower:
                        db_type = "PostgreSQL"
                    elif "mysql" in image_lower:
                        db_type = "MySQL"
                    elif "mongo" in image_lower:
                        db_type = "MongoDB"
                    else:
                        db_type = "Database"

                    rel_compose = compose_path.relative_to(root).as_posix()
                    databases.append(
                        {
                            "service_name": s_name,
                            "db_type": db_type,
                            "image": image,
                            "port": host_port,
                            "db_name": db_name,
                            "db_user": db_user,
                            "db_password": db_password,
                            "compose_file": f"./{rel_compose}",
                        }
                    )
            except Exception:
                pass

    return databases


def generate_agent_context(root_path: Union[str, Path] = ".") -> bool:
    """
    Scans the repository and generates AGENTS.md, CLAUDE.md, and .cursorrules.
    """
    root = Path(root_path).resolve()
    if not root.exists() or not root.is_dir():
        return False

    try:
        discovered = discover_docker_projects(root)
    except Exception:
        discovered = []

    services: List[Dict[str, Any]] = []
    backends: List[Dict[str, Any]] = []
    frontends: List[Dict[str, Any]] = []

    for p in discovered:
        meta = FRAMEWORK_METADATA.get(
            p.kind,
            {
                "framework": p.kind.capitalize(),
                "category": "backend",
                "default_port": 8080,
                "run_cmd": "devctl run",
                "test_cmd": "npm test",
            },
        )
        port = _detect_service_port(p.path, p.kind, meta["default_port"])
        try:
            rel_path = f"./{p.path.relative_to(root).as_posix()}"
        except ValueError:
            rel_path = f"./{p.name}"

        service_data = {
            "name": p.name,
            "kind": p.kind,
            "framework": meta["framework"],
            "category": meta["category"],
            "relative_path": rel_path,
            "port": port,
            "run_cmd": meta["run_cmd"],
            "test_cmd": meta["test_cmd"],
        }
        services.append(service_data)
        if meta["category"] == "backend":
            backends.append(service_data)
        else:
            frontends.append(service_data)

    databases = _discover_databases(root)

    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)

    context = {
        "services": services,
        "backends": backends,
        "frontends": frontends,
        "databases": databases,
    }

    try:
        agents_tpl = env.get_template("AGENTS.md.j2")
        claude_tpl = env.get_template("CLAUDE.md.j2")
        cursor_tpl = env.get_template(".cursorrules.j2")

        (root / "AGENTS.md").write_text(agents_tpl.render(context), encoding="utf-8")
        (root / "CLAUDE.md").write_text(claude_tpl.render(context), encoding="utf-8")
        (root / ".cursorrules").write_text(cursor_tpl.render(context), encoding="utf-8")

        typer.secho(
            "Agent context generated (AGENTS.md, CLAUDE.md, .cursorrules).",
            fg=typer.colors.CYAN,
        )
        return True
    except Exception as e:
        typer.secho(f"Warning: Failed to generate agent context: {e}", fg=typer.colors.YELLOW)
        return False
