"""
Local development environment runner.
Handles parallel process management for multi-tier applications with log prefixing.
"""

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.markup import escape

from devctl.generators.docker_scaffold import DockerProject
from devctl.utils import get_platform
from devctl.utils.env_loader import get_project_env

console = Console()

# Global list to track processes for cleanup
active_processes = []
active_threads = []


def is_docker_running():
    """Checks if the Docker daemon is active on the system."""
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def stream_logs(name: str, process: subprocess.Popen, color: str):
    """Streams logs from a process with a colored prefix."""
    try:
        # Use line-buffered reading
        for line in iter(process.stdout.readline, b""):
            if line:
                decoded_line = line.decode("utf-8", errors="ignore").rstrip()
                console.print(f"[{color}]{name:>15} |[/{color}] {escape(decoded_line)}")
    except Exception as e:
        console.print(f"[red]Error streaming logs for {name}: {escape(str(e))}[/red]")


def _launch_process(p: DockerProject, cmd: List[str], color: str, label: str):
    """Helper to launch a process with log streaming and .env loading."""
    global active_processes, active_threads

    typer.secho(f"Starting {label}: {p.name}...", fg=getattr(typer.colors, color.upper()))

    # Load environment variables including .env if present
    env = get_project_env(p.path)

    platform = get_platform()
    proc = subprocess.Popen(
        cmd,
        cwd=str(p.path),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        env=env,
        shell=platform.shell_required,
    )
    active_processes.append((p.name, proc))

    t = threading.Thread(target=stream_logs, args=(p.name, proc, color), daemon=True)
    t.start()
    active_threads.append(t)


def launch_dev_environment(projects: List[DockerProject], docker_composes: List[Path]):
    """
    Launches the necessary processes in parallel with structured startup and log streaming.
    """
    global active_processes

    def signal_handler(_sig, _frame):
        typer.echo("\nShutdown requested. Cleaning up...")
        cleanup_and_exit(docker_composes)

    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)
    else:
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, signal_handler)

    try:
        # 1. Start Databases
        if docker_composes:
            if not is_docker_running():
                typer.secho("Error: Docker service is not running.", fg=typer.colors.RED)
                sys.exit(1)

            for compose_path in docker_composes:
                typer.secho(
                    f"Starting Docker Compose DB in {compose_path}...",
                    fg=typer.colors.CYAN,
                )
                subprocess.run(
                    ["docker", "compose", "-f", "docker-compose-db.yml", "up", "-d"],
                    cwd=str(compose_path),
                    check=True,
                )

            typer.echo("Waiting 5s for databases to initialize...")
            time.sleep(5)

        platform = get_platform()
        # 2. Start Projects
        for p in projects:
            if p.kind == "spring":
                _launch_process(p, [platform.mvnw_cmd, "spring-boot:run"], "green", "Spring Boot")

            elif p.kind == "angular":
                _launch_process(p, ["npx", "ng", "serve"], "cyan", "Angular")

            elif p.kind == "vue":
                _launch_process(p, ["npm", "run", "dev"], "magenta", "Vue")

            elif p.kind == "react":
                _launch_process(p, ["npm", "run", "dev"], "blue", "React")

            elif p.kind == "nextjs":
                _launch_process(p, ["npm", "run", "dev"], "yellow", "NextJS")

            elif p.kind == "svelte":
                _launch_process(p, ["npm", "run", "dev"], "red", "Svelte")

            elif p.kind == "nest":
                _launch_process(p, ["npm", "run", "start:dev"], "magenta", "NestJS")

            elif p.kind == "nodejs":
                _launch_process(p, ["npm", "run", "dev"], "green", "NodeJS")

            elif p.kind == "fastapi":
                venv_python = platform.get_venv_python(p.path)
                if not os.path.exists(venv_python):
                    venv_python = platform.python_exe
                _launch_process(
                    p, [venv_python, "-m", "uvicorn", "main:app", "--reload"], "cyan", "FastAPI"
                )

            elif p.kind == "django":
                venv_python = platform.get_venv_python(p.path)
                if not os.path.exists(venv_python):
                    venv_python = platform.python_exe
                _launch_process(p, [venv_python, "manage.py", "runserver"], "green", "Django")

            elif p.kind == "go":
                _launch_process(p, ["go", "run", "."], "cyan", "Go")

        if not active_processes and not docker_composes:
            typer.secho(
                "Warning: No projects or databases detected to run.",
                fg=typer.colors.YELLOW,
            )
            return

        typer.secho(
            "\nDevelopment environment active! Press Ctrl+C to stop everything gracefully.\n",
            fg=typer.colors.GREEN,
            bold=True,
        )
        # Keep the main thread alive
        while True:
            # Monitor process health
            for name, proc in active_processes:
                exit_code = proc.poll()
                if exit_code is not None:
                    typer.secho(
                        f"\nError: {name} process terminated unexpectedly "
                        f"(Exit code: {exit_code}).",
                        fg=typer.colors.RED,
                        bold=True,
                    )
                    # Trigger shutdown logic
                    raise KeyboardInterrupt

            time.sleep(1)
            # Check if any process has died unexpectedly
            # This is a bit redundant with the monitor above but kept for compatibility
            for name, proc in active_processes:
                if proc.poll() is not None:
                    typer.secho(
                        f"Warning: Process {name} exited with code {proc.returncode}",
                        fg=typer.colors.RED,
                    )
                    active_processes.remove((name, proc))

    except Exception as e:
        typer.secho(f"Error: A system error occurred: {e}", fg=typer.colors.RED)
        cleanup_and_exit(docker_composes)


def cleanup_and_exit(docker_composes: List[Path]):
    """Stops all active processes and docker containers."""
    platform = get_platform()
    for name, proc in active_processes:
        typer.echo(f"Closing {name}...")
        platform.kill_process_tree(proc)

    for compose_path in docker_composes:
        typer.echo(f"Stopping Docker Compose DB in {compose_path}...")
        try:
            subprocess.run(
                ["docker", "compose", "-f", "docker-compose-db.yml", "down", "-v"],
                cwd=str(compose_path),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            typer.secho(f"Warning: Docker cleanup failed for {compose_path}", fg=typer.colors.RED)

    typer.secho("Cleanup finished. Environment is clean.", fg=typer.colors.GREEN)
    sys.exit(0)
