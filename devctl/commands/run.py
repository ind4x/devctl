"""
CLI command group for running the local development environment.
Automatically detects and launches backend, frontend, and database services.
"""

from pathlib import Path

import typer

from devctl.generators.docker import discover_docker_projects
from devctl.orchestrator.runner import launch_dev_environment
from devctl.utils.dependencies import check_tool

app = typer.Typer(help="Local execution and development commands.")


@app.callback(invoke_without_command=True)
def run_env(ctx: typer.Context):
    """
    Scans the current tree and automatically launches Spring, Angular, Vue, and Databases.
    """
    if ctx.invoked_subcommand is not None:
        return

    typer.secho("Analyzing the current directory tree...", fg=typer.colors.CYAN)

    projects = discover_docker_projects(".")

    # Check for docker-compose-db.yml files
    docker_composes = []
    for p in Path(".").rglob("docker-compose-db.yml"):
        if "node_modules" not in str(p) and "target" not in str(p) and ".git" not in str(p):
            docker_composes.append(p.parent)

    any(p.kind == "spring" for p in projects)
    any(p.kind == "angular" for p in projects)
    any(p.kind == "vue" for p in projects)
    has_docker = len(docker_composes) > 0

    # Check dependencies based on detection
    if has_docker:
        check_tool("docker", "running the database environment")

    # Group counts
    counts = {}
    for p in projects:
        counts[p.kind] = counts.get(p.kind, 0) + 1

    # Visual summary of detection for the user
    def get_status(condition: bool):
        return (
            typer.style("FOUND", fg=typer.colors.GREEN)
            if condition
            else typer.style("MISSING", fg=typer.colors.RED)
        )

    typer.echo(f"  - Docker Compose DB ({len(docker_composes)}) : {get_status(has_docker)}")

    for kind in sorted(counts.keys()):
        typer.echo(f"  - {kind.capitalize()} ({counts[kind]}) : {get_status(True)}")

    if not projects and not docker_composes:
        typer.secho("\nError: No valid development environment detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Transfer control to the system orchestration layer
    launch_dev_environment(projects, docker_composes)
