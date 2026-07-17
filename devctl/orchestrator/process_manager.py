import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import psutil

from devctl.generators.docker_scaffold import DockerProject
from devctl.utils import get_platform
from devctl.utils.env_loader import get_project_env


@dataclass
class ServiceState:
    name: str
    kind: str  # spring, angular, vue, react, nextjs, svelte, nest, nodejs, fastapi, django, go,
    # docker-db
    path: Path
    cmd: List[str]
    process: Optional[subprocess.Popen] = None
    status: str = "STOPPED"  # RUNNING, STOPPED, CRASHED, STARTING
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    logs: List[str] = field(default_factory=list)
    log_lock: threading.Lock = field(default_factory=threading.Lock)
    color: str = "white"


class ProcessManager:
    def __init__(self, projects: List[DockerProject], docker_composes: List[Path]):
        self.projects = projects
        self.docker_composes = docker_composes
        self.services: Dict[str, ServiceState] = {}
        self._init_services()

    def _init_services(self):
        platform = get_platform()
        # 1. Register Docker databases
        for compose_path in self.docker_composes:
            name = f"db-{compose_path.name or 'compose'}"
            # Use docker command as standard
            cmd = ["docker", "compose", "-f", "docker-compose-db.yml", "up"]
            self.services[name] = ServiceState(
                name=name, kind="docker-db", path=compose_path, cmd=cmd, color="cyan"
            )

        # 2. Register projects
        for p in self.projects:
            cmd = self._resolve_cmd(p, platform)
            color = self._resolve_color(p.kind)
            self.services[p.name] = ServiceState(
                name=p.name, kind=p.kind, path=p.path, cmd=cmd, color=color
            )

    def _resolve_cmd(self, p: DockerProject, platform) -> List[str]:
        if p.kind == "spring":
            return [platform.mvnw_cmd, "spring-boot:run"]
        elif p.kind == "angular":
            return ["npx", "ng", "serve"]
        elif p.kind == "vue":
            return ["npm", "run", "dev"]
        elif p.kind == "react":
            return ["npm", "run", "dev"]
        elif p.kind == "nextjs":
            return ["npm", "run", "dev"]
        elif p.kind == "svelte":
            return ["npm", "run", "dev"]
        elif p.kind == "nest":
            return ["npm", "run", "start:dev"]
        elif p.kind == "nodejs":
            return ["npm", "run", "dev"]
        elif p.kind == "fastapi":
            venv_python = platform.get_venv_python(p.path)
            if not os.path.exists(venv_python):
                venv_python = platform.python_exe
            return [venv_python, "-m", "uvicorn", "main:app", "--reload"]
        elif p.kind == "django":
            venv_python = platform.get_venv_python(p.path)
            if not os.path.exists(venv_python):
                venv_python = platform.python_exe
            return [venv_python, "manage.py", "runserver"]
        elif p.kind == "go":
            return ["go", "run", "."]
        return ["echo", "Unknown kind"]

    def _resolve_color(self, kind: str) -> str:
        colors = {
            "spring": "green",
            "angular": "cyan",
            "vue": "magenta",
            "react": "blue",
            "nextjs": "yellow",
            "svelte": "red",
            "nest": "magenta",
            "nodejs": "green",
            "fastapi": "cyan",
            "django": "green",
            "go": "cyan",
        }
        return colors.get(kind, "white")

    def start_service(self, name: str):
        service = self.services.get(name)
        if not service or service.status in ("RUNNING", "STARTING"):
            return

        service.status = "STARTING"
        service.cpu_percent = 0.0
        service.memory_mb = 0.0

        # Launch DB or regular project
        if service.kind == "docker-db":
            t = threading.Thread(target=self._run_docker_db, args=(service,), daemon=True)
            t.start()
        else:
            t = threading.Thread(target=self._run_project_process, args=(service,), daemon=True)
            t.start()

    def _run_docker_db(self, service: ServiceState):
        try:
            self._log_to_service(service, "Starting Docker Compose database...\n")
            # Run docker compose up
            proc = subprocess.Popen(
                ["docker", "compose", "-f", "docker-compose-db.yml", "up"],
                cwd=str(service.path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
            )
            service.process = proc
            service.status = "RUNNING"
            self._stream_logs_thread(service)
        except Exception as e:
            service.status = "CRASHED"
            self._log_to_service(service, f"Error starting Docker DB: {e}\n")

    def _run_project_process(self, service: ServiceState):
        try:
            env = get_project_env(service.path)
            platform = get_platform()
            self._log_to_service(service, f"Launching process: {' '.join(service.cmd)}\n")
            proc = subprocess.Popen(
                service.cmd,
                cwd=str(service.path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                env=env,
                shell=platform.shell_required,
            )
            service.process = proc
            service.status = "RUNNING"
            self._stream_logs_thread(service)
        except Exception as e:
            service.status = "CRASHED"
            self._log_to_service(service, f"Error launching process: {e}\n")

    def _stream_logs_thread(self, service: ServiceState):
        try:
            # Use line-buffered reading
            for line in iter(service.process.stdout.readline, b""):
                if line:
                    decoded = line.decode("utf-8", errors="ignore").rstrip()
                    self._log_to_service(service, decoded)

            # Subprocess finished
            ret = service.process.wait()
            if ret != 0 and service.status != "STOPPED":
                service.status = "CRASHED"
                self._log_to_service(service, f"\nProcess exited unexpectedly with code {ret}")
            else:
                service.status = "STOPPED"
                self._log_to_service(service, "\nProcess stopped.")
        except Exception as e:
            self._log_to_service(service, f"\nError streaming logs: {e}")
            service.status = "CRASHED"

    def _log_to_service(self, service: ServiceState, message: str):
        with service.log_lock:
            service.logs.append(message)
            if len(service.logs) > 2000:
                service.logs.pop(0)

    def stop_service(self, name: str):
        service = self.services.get(name)
        if not service:
            return

        if service.kind == "docker-db":
            service.status = "STOPPING"
            self._log_to_service(service, "Shutting down Docker Compose database...\n")
            try:
                subprocess.run(
                    ["docker", "compose", "-f", "docker-compose-db.yml", "down"],
                    cwd=str(service.path),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                self._log_to_service(service, f"Error stopping database: {e}\n")
            if service.process:
                try:
                    service.process.terminate()
                except Exception:
                    pass
            service.status = "STOPPED"
        else:
            if not service.process or service.status == "STOPPED":
                return

            service.status = "STOPPING"
            self._log_to_service(service, "Stopping service process tree...\n")
            try:
                platform = get_platform()
                platform.kill_process_tree(service.process)
            except Exception as e:
                self._log_to_service(service, f"Error stopping process: {e}\n")
            service.status = "STOPPED"

    def restart_service(self, name: str):
        self.stop_service(name)
        time.sleep(0.5)
        self.start_service(name)

    def update_metrics(self):
        for service in self.services.values():
            if service.process and service.process.poll() is None:
                if service.kind == "docker-db":
                    service.status = "RUNNING"
                    service.cpu_percent = 0.0
                    service.memory_mb = 0.0
                    continue

                try:
                    p = psutil.Process(service.process.pid)
                    children = p.children(recursive=True)
                    cpu = p.cpu_percent()
                    mem = p.memory_info().rss
                    for child in children:
                        try:
                            cpu += child.cpu_percent()
                            mem += child.memory_info().rss
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    service.cpu_percent = cpu
                    service.memory_mb = mem / (1024 * 1024)
                    service.status = "RUNNING"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    service.status = "CRASHED"
            else:
                if service.status == "RUNNING":
                    service.status = "CRASHED"
                service.cpu_percent = 0.0
                service.memory_mb = 0.0

    def cleanup_all(self):
        for name in list(self.services.keys()):
            self.stop_service(name)
