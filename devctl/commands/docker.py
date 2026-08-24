"""
CLI command group for Docker-related operations.
Includes scaffolding Dockerfiles for detected services.
"""

from pathlib import Path

import typer

from devctl.generators.docker import (
    DockerScaffoldError,
    scaffold_docker_assets,
)

PATH_ARGUMENT = typer.Argument(
    Path("."),
    help="Repository or project directory to scan for Dockerizable services.",
)
FORCE_OPTION = typer.Option(
    False,
    "--force",
    help="Overwrite generated Docker files that already exist.",
)
DRY_RUN_OPTION = typer.Option(
    False,
    "--dry-run",
    help="Show what would be generated without writing files.",
)


def dockerize(
    path: Path = PATH_ARGUMENT,
    force: bool = FORCE_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
):
    """
    Scaffold Dockerfiles for Spring Boot, Angular, and Vue/Vite projects.
    """
    try:
        result = scaffold_docker_assets(
            path,
            force=force,
            dry_run=dry_run,
        )
    except DockerScaffoldError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    mode = "Dry run" if dry_run else "Docker scaffolding"
    typer.secho(f"{mode} complete for {result.root_path}", fg=typer.colors.CYAN, bold=True)

    typer.echo("\nDetected services:")
    for service in result.services:
        typer.echo(f"  - {service.kind}: {service.service_name} ({service.relative_context})")

    typer.echo("\nFiles:")
    for operation in result.operations:
        relative_path = operation.path.relative_to(result.root_path)
        typer.echo(f"  - {operation.action}: {relative_path}")

    typer.secho(
        f"\nSummary: {result.created_count} created, "
        f"{result.skipped_count} skipped, {result.planned_count} planned.",
        fg=typer.colors.GREEN,
    )
