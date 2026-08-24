"""Dockerfile scaffolding for supported devctl projects."""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from jinja2 import Environment, FileSystemLoader

IGNORED_DIRECTORIES = {
    ".angular",
    ".git",
    ".mvn",
    ".next",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "venv",
}


class DockerScaffoldError(Exception):
    """Raised when Dockerfile scaffolding cannot be completed."""


@dataclass(frozen=True)
class DockerProject:
    """A project that can receive a generated Dockerfile."""

    kind: str
    path: Path
    name: str
    service_name: str
    relative_context: str
    java_version: Optional[str] = None
    node_version: Optional[str] = None
    angular_output_name: Optional[str] = None


@dataclass(frozen=True)
class FileOperation:
    """A single file operation performed or planned by the scaffold command."""

    path: Path
    action: str


@dataclass(frozen=True)
class DockerScaffoldResult:
    """Summary returned after Dockerfile scaffolding."""

    root_path: Path
    services: list[DockerProject]
    operations: list[FileOperation]

    @property
    def created_count(self) -> int:
        return sum(1 for operation in self.operations if operation.action == "created")

    @property
    def skipped_count(self) -> int:
        return sum(1 for operation in self.operations if operation.action == "skipped")

    @property
    def planned_count(self) -> int:
        return sum(1 for operation in self.operations if operation.action.startswith("would_"))


def sanitize_service_name(raw_name: str, fallback: str = "service") -> str:
    """Return a lowercase Docker-friendly service name."""
    service_name = re.sub(r"[^a-z0-9-]+", "-", raw_name.lower()).strip("-")
    service_name = re.sub(r"-{2,}", "-", service_name)
    return service_name or fallback


def discover_docker_projects(root_path: Union[str, Path]) -> list[DockerProject]:
    """Discover all supported projects under ``root_path``."""
    root = Path(root_path).resolve()
    if not root.exists():
        raise DockerScaffoldError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise DockerScaffoldError(f"Path is not a directory: {root}")

    candidates: list[tuple[str, Path]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRECTORIES]

        project_path = Path(dirpath)
        filename_set = set(filenames)

        if "pom.xml" in filename_set:
            candidates.append(("spring", project_path))
        if "angular.json" in filename_set:
            candidates.append(("angular", project_path))

        has_vite_config = {"vite.config.ts", "vite.config.js"} & filename_set
        if has_vite_config and "angular.json" not in filename_set:
            # Check package.json to distinguish between vue and react
            pkg_path = project_path / "package.json"
            if pkg_path.exists():
                try:
                    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                    deps = pkg.get("dependencies", {})
                    dev_deps = pkg.get("devDependencies", {})
                    all_deps = {**deps, **dev_deps}

                    if "vue" in all_deps:
                        candidates.append(("vue", project_path))
                    elif "react" in all_deps:
                        candidates.append(("react", project_path))
                    else:
                        candidates.append(("vue", project_path))  # Fallback to vue
                except Exception:
                    candidates.append(("vue", project_path))
            else:
                candidates.append(("vue", project_path))

        if "nest-cli.json" in filename_set:
            candidates.append(("nest", project_path))

        if any(f.startswith("next.config.") for f in filename_set):
            candidates.append(("nextjs", project_path))

        if "svelte.config.js" in filename_set:
            candidates.append(("svelte", project_path))

        if "main.py" in filename_set and "requirements.txt" in filename_set:
            try:
                reqs = (project_path / "requirements.txt").read_text(encoding="utf-8")
                if "fastapi" in reqs.lower():
                    candidates.append(("fastapi", project_path))
                elif "django" in reqs.lower():
                    candidates.append(("django", project_path))
            except (OSError, UnicodeDecodeError):
                # Best-effort discovery: unreadable requirements files should not stop scanning.
                pass

        if "manage.py" in filename_set and "requirements.txt" in filename_set:
            try:
                reqs = (project_path / "requirements.txt").read_text(encoding="utf-8")
                if "django" in reqs.lower():
                    candidates.append(("django", project_path))
            except (OSError, UnicodeDecodeError):
                # Best-effort discovery: ignore unreadable/invalid requirements.txt here.
                pass

        if "go.mod" in filename_set:
            candidates.append(("go", project_path))

        if "package.json" in filename_set and not any(
            k in ["angular", "vue", "react", "nest", "nextjs", "svelte"]
            for k, p in candidates
            if p == project_path
        ):
            candidates.append(("nodejs", project_path))

    used_names: set[str] = set()
    projects: list[DockerProject] = []

    for kind, project_path in sorted(candidates, key=lambda item: (str(item[1]), item[0])):
        name = _project_name(kind, project_path)
        service_name = _unique_service_name(name, used_names, fallback=kind)
        used_names.add(service_name)

        projects.append(
            DockerProject(
                kind=kind,
                path=project_path,
                name=name,
                service_name=service_name,
                relative_context=_relative_context(root, project_path),
                java_version=_spring_java_version(project_path) if kind == "spring" else None,
                node_version=(
                    _node_version(project_path, kind)
                    if kind in {"angular", "vue", "react", "nest", "nodejs", "nextjs", "svelte"}
                    else None
                ),
                angular_output_name=(
                    _angular_output_name(project_path) if kind == "angular" else None
                ),
            )
        )

    return projects


def scaffold_docker_assets(
    root_path: Union[str, Path] = ".",
    *,
    force: bool = False,
    dry_run: bool = False,
) -> DockerScaffoldResult:
    """Generate Dockerfiles and docker-compose-prod.yml for all supported projects in a tree."""
    root = Path(root_path).resolve()
    projects = discover_docker_projects(root)
    if not projects:
        raise DockerScaffoldError("No supported project detected.")

    env = _template_environment()
    operations = [
        _write_file(
            project.path / "Dockerfile",
            _dockerfile_content(env, project),
            force=force,
            dry_run=dry_run,
        )
        for project in projects
    ]

    # Also scaffold the global docker-compose-prod.yml
    compose_path = root / "docker-compose-prod.yml"
    compose_content = _generate_compose_content(projects)
    operations.append(
        _write_file(
            compose_path,
            compose_content,
            force=force,
            dry_run=dry_run,
        )
    )

    return DockerScaffoldResult(root_path=root, services=projects, operations=operations)


def _generate_compose_content(projects: list[DockerProject]) -> str:
    services_data = []
    databases = []
    seen_db_names = set()

    for project in projects:
        service_dict = {
            "service_name": project.service_name,
            "kind": project.kind,
            "relative_context": project.relative_context,
            "db": None,
        }

        if project.kind == "spring":
            db_info = extract_db_info(project.path)
            if db_info:
                service_dict["db"] = db_info
                if db_info["service_name"] not in seen_db_names:
                    databases.append(db_info)
                    seen_db_names.add(db_info["service_name"])

        services_data.append(service_dict)

    template_dir = Path(__file__).resolve().parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("deploy.yml.j2")
    return template.render(services=services_data, databases=databases)


def extract_db_info(project_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract database information from a Spring Boot project's application.properties.
    """
    props_path = project_path / "src" / "main" / "resources" / "application.properties"
    if not props_path.exists():
        # Fallback to checking for docker-compose-db.yml in the same dir
        return extract_db_from_compose(project_path / "docker-compose-db.yml")

    content = props_path.read_text(encoding="utf-8", errors="ignore")

    # spring.datasource.url=jdbc:postgresql://localhost:5432/sample_api_db
    url_match = re.search(r"spring\.datasource\.url=jdbc:([^:]+)://[^:]+:(\d+)/([\w-]+)", content)
    # spring.data.mongodb.uri=mongodb://admin:password@localhost:27017/db_name
    mongo_match = re.search(
        r"spring\.data\.mongodb\.uri=mongodb://([^:]+):([^@]+)@[^:]+:(\d+)/([\w-]+)", content
    )

    user_match = re.search(r"spring\.datasource\.username=([\w-]+)", content)
    pass_match = re.search(r"spring\.datasource\.password=([\w-]+)", content)

    if not url_match and not mongo_match:
        return extract_db_from_compose(project_path / "docker-compose-db.yml")

    if mongo_match:
        db_type = "mongodb"
        db_user = mongo_match.group(1)
        db_pass = mongo_match.group(2)
        db_port = mongo_match.group(3)
        db_name = mongo_match.group(4)
    else:
        db_type_raw = url_match.group(1)
        db_type = "postgresql" if "postgres" in db_type_raw else "mysql"
        db_port = url_match.group(2)
        db_name = url_match.group(3)
        db_user = user_match.group(1) if user_match else "admin"
        db_pass = pass_match.group(1) if pass_match else "password"

    db_dict = _build_db_dict(db_type, db_port, db_name, db_user, db_pass)

    # Try to refine service name from existing docker-compose if possible
    compose_path = project_path / "docker-compose-db.yml"
    if compose_path.exists():
        try:
            with open(compose_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "services" in config:
                    # Find the first service that looks like a database
                    for s_name, s_cfg in config["services"].items():
                        image = str(s_cfg.get("image", ""))
                        if db_type == "postgresql" and "postgres" in image:
                            db_dict["service_name"] = s_name
                            break
                        if db_type == "mysql" and "mysql" in image:
                            db_dict["service_name"] = s_name
                            break
                        if db_type == "mongodb" and "mongo" in image:
                            db_dict["service_name"] = s_name
                            break
        except (OSError, yaml.YAMLError):
            pass

    return db_dict


def extract_db_from_compose(compose_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract database information from a docker-compose-db.yml file using PyYAML.
    """
    if not compose_path.exists():
        return None

    try:
        with open(compose_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception:
        return None

    if not config or "services" not in config:
        return None

    for service_name, service_cfg in config["services"].items():
        image = str(service_cfg.get("image", ""))
        if "postgres" in image or "mysql" in image or "mongo" in image:
            if "postgres" in image:
                db_type = "postgresql"
            elif "mysql" in image:
                db_type = "mysql"
            else:
                db_type = "mongodb"

            env = service_cfg.get("environment", {})
            env_dict = {}
            if isinstance(env, list):
                for item in env:
                    if "=" in item:
                        k, v = item.split("=", 1)
                        env_dict[k] = v
                    elif ":" in item:
                        k, v = item.split(":", 1)
                        env_dict[k] = v.strip()
            elif isinstance(env, dict):
                env_dict = env

            if db_type == "postgresql":
                user = env_dict.get("POSTGRES_USER", "admin")
                password = env_dict.get("POSTGRES_PASSWORD", "password")
                db_name = env_dict.get("POSTGRES_DB", "db")
            elif db_type == "mysql":
                user = env_dict.get("MYSQL_USER", env_dict.get("MYSQL_ROOT_PASSWORD", "admin"))
                password = env_dict.get(
                    "MYSQL_PASSWORD", env_dict.get("MYSQL_ROOT_PASSWORD", "password")
                )
                db_name = env_dict.get("MYSQL_DATABASE", "db")
            else:
                user = env_dict.get("MONGO_INITDB_ROOT_USERNAME", "admin")
                password = env_dict.get("MONGO_INITDB_ROOT_PASSWORD", "password")
                db_name = env_dict.get("MONGO_INITDB_DATABASE", "db")

            ports = service_cfg.get("ports", [])
            host_port = None
            if ports and isinstance(ports, list):
                first_port = str(ports[0])
                if ":" in first_port:
                    host_port = first_port.split(":")[0].strip("'").strip('"')

            db_dict = _build_db_dict(
                db_type,
                host_port
                or (
                    "5432"
                    if db_type == "postgresql"
                    else ("3306" if db_type == "mysql" else "27017")
                ),
                db_name,
                user,
                password,
            )
            db_dict["service_name"] = service_name
            return db_dict

    return None


def _build_db_dict(db_type: str, port: str, name: str, user: str, password: str) -> Dict[str, Any]:
    is_postgres = db_type == "postgresql"
    is_mysql = db_type == "mysql"

    if is_postgres:
        internal_port = "5432"
        image = "postgres:15-alpine"
        vol_path = "/var/lib/postgresql/data"
    elif is_mysql:
        internal_port = "3306"
        image = "mysql:8.0"
        vol_path = "/var/lib/mysql/data"
    else:
        internal_port = "27017"
        image = "mongo:6.0"
        vol_path = "/data/db"

    env = {}
    if is_postgres:
        env = {
            "POSTGRES_USER": user,
            "POSTGRES_PASSWORD": password,
            "POSTGRES_DB": name,
        }
    elif is_mysql:
        env = {
            "MYSQL_ROOT_PASSWORD": password,
            "MYSQL_DATABASE": name,
            "MYSQL_USER": user,
            "MYSQL_PASSWORD": password,
        }
    else:
        env = {
            "MONGO_INITDB_ROOT_USERNAME": user,
            "MONGO_INITDB_ROOT_PASSWORD": password,
            "MONGO_INITDB_DATABASE": name,
        }

    return {
        "type": db_type,
        "port": port,
        "internal_port": internal_port,
        "name": name,
        "user": user,
        "password": password,
        "service_name": f"{name}-db",
        "image": image,
        "volume_name": f"{name}_data",
        "volume_path": vol_path,
        "env": env,
    }


def _dockerfile_content(env: Environment, project: DockerProject) -> str:
    if project.kind == "spring":
        return env.get_template("spring/Dockerfile.j2").render(project=project)
    if project.kind == "nest":
        return env.get_template("nestjs/Dockerfile.j2").render(project=project)
    if project.kind == "nodejs":
        return env.get_template("nodejs/Dockerfile.j2").render(project=project)
    if project.kind == "nextjs":
        return env.get_template("nextjs/Dockerfile.j2").render(project=project)
    if project.kind == "fastapi":
        return env.get_template("fastapi/Dockerfile.j2").render(project=project)
    if project.kind == "django":
        return env.get_template("django/Dockerfile.j2").render(project=project)
    if project.kind == "svelte":
        return env.get_template("svelte/Dockerfile.j2").render(project=project)
    if project.kind == "go":
        return env.get_template("go/Dockerfile.j2").render(project=project)
    return env.get_template("frontend/Dockerfile.j2").render(project=project)


def _write_file(path: Path, content: str, *, force: bool, dry_run: bool) -> FileOperation:
    content = content.rstrip() + "\n"
    exists = path.exists()

    if exists and not force:
        return FileOperation(path=path, action="skipped")

    if dry_run:
        action = "would_overwrite" if exists else "would_create"
        return FileOperation(path=path, action=action)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return FileOperation(path=path, action="overwritten" if exists else "created")


def _template_environment() -> Environment:
    template_dir = Path(__file__).resolve().parent / "templates"
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def _project_name(kind: str, project_path: Path) -> str:
    if kind == "spring":
        return _spring_artifact_id(project_path) or project_path.name
    if kind == "angular":
        return (
            _angular_output_name(project_path) or _package_name(project_path) or project_path.name
        )
    return _package_name(project_path) or project_path.name


def _unique_service_name(raw_name: str, used_names: set[str], fallback: str) -> str:
    base_name = sanitize_service_name(raw_name, fallback=fallback)
    if base_name not in used_names:
        return base_name

    index = 2
    while f"{base_name}-{index}" in used_names:
        index += 1
    return f"{base_name}-{index}"


def _relative_context(root: Path, project_path: Path) -> str:
    try:
        relative = project_path.relative_to(root)
    except ValueError:
        relative = Path(os.path.relpath(project_path, root))

    if str(relative) == ".":
        return "."
    return f"./{relative.as_posix()}"


def _spring_artifact_id(project_path: Path) -> Optional[str]:
    pom_path = project_path / "pom.xml"
    if not pom_path.exists():
        return None

    try:
        root = ET.parse(pom_path).getroot()
    except ET.ParseError:
        return None

    for child in root:
        if _local_name(child.tag) == "artifactId" and child.text:
            return child.text.strip()
    return None


def _spring_java_version(project_path: Path) -> str:
    pom_path = project_path / "pom.xml"
    if not pom_path.exists():
        return "17"

    content = pom_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<java\.version>\s*([^<\s]+)\s*</java\.version>", content)
    if match:
        version = match.group(1)
        major = re.match(r"\d+", version)
        if major:
            return major.group(0)
    return "17"


def _angular_output_name(project_path: Path) -> Optional[str]:
    angular_json = project_path / "angular.json"
    if not angular_json.exists():
        return None

    try:
        config = json.loads(angular_json.read_text(encoding="utf-8"))
        projects = config.get("projects", {})
    except (json.JSONDecodeError, OSError):
        return None

    if isinstance(projects, dict) and projects:
        return str(next(iter(projects.keys())))
    return None


def _package_name(project_path: Path) -> Optional[str]:
    package_json = _read_package_json(project_path)
    name = package_json.get("name")
    return str(name) if name else None


def _node_version(project_path: Path, kind: str) -> str:
    package_json = _read_package_json(project_path)
    engines = package_json.get("engines", {})
    node_range = str(engines.get("node", "")) if isinstance(engines, dict) else ""

    engine_major = _highest_supported_node_major(node_range)
    if engine_major:
        return engine_major

    if kind == "angular":
        angular_major = _angular_major(package_json)
        if angular_major >= 20:
            return "22"
        if angular_major >= 17:
            return "20"
        return "18"

    if kind in ["nest", "nodejs", "nextjs", "svelte"]:
        return "20"

    return "22"


def _read_package_json(project_path: Path) -> dict[str, Any]:
    package_path = project_path / "package.json"
    if not package_path.exists():
        return {}

    try:
        content = json.loads(package_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    return content if isinstance(content, dict) else {}


def _highest_supported_node_major(node_range: str) -> Optional[str]:
    supported = {18, 20, 22, 24}
    majors = {int(value) for value in re.findall(r"(?<!\.)\b(18|20|22|24)\b", node_range)}
    usable = sorted(majors & supported)
    return str(usable[-1]) if usable else None


def _angular_major(package_json: dict[str, Any]) -> int:
    sections = ["dependencies", "devDependencies"]
    for section in sections:
        dependencies = package_json.get(section, {})
        if not isinstance(dependencies, dict):
            continue
        version = dependencies.get("@angular/core") or dependencies.get("@angular/cli")
        if version:
            match = re.search(r"(\d+)", str(version))
            if match:
                return int(match.group(1))
    return 20


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
