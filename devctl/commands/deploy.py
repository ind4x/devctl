from pathlib import Path

import typer

from devctl.generators.docker_scaffold import (
    DockerScaffoldError,
    scaffold_docker_assets,
)

app = typer.Typer(help="Deployment and orchestration commands.")

PATH_ARGUMENT = typer.Argument(
    Path("."),
    help="Repository or project directory to scan for services.",
)

FORCE_OPTION = typer.Option(
    False,
    "--force",
    help="Overwrite generated Docker files that already exist.",
)


@app.command()
def deploy(
    path: Path = PATH_ARGUMENT,
    force: bool = FORCE_OPTION,
):
    """
    Generate a global docker-compose-prod.yml by scanning subdirectories.
    """
    typer.secho(f"Preparing deployment for {path.resolve()}...", fg=typer.colors.CYAN, bold=True)

    try:
        result = scaffold_docker_assets(
            path,
            force=force,
        )
    except DockerScaffoldError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    typer.secho(
        f"Deployment scaffolding complete for {result.root_path}",
        fg=typer.colors.CYAN,
        bold=True,
    )

    typer.echo("\nDetected services:")
    for service in result.services:
        typer.echo(f"  - {service.kind}: {service.service_name} ({service.relative_context})")

    typer.echo("\nFiles:")
    for operation in result.operations:
        if "docker-compose-prod.yml" in str(operation.path):
            relative_path = operation.path.relative_to(result.root_path)
            typer.echo(f"  - {operation.action}: {relative_path}")

    typer.secho(
        f"\nSummary: {result.created_count} created, {result.skipped_count} skipped.",
        fg=typer.colors.GREEN,
    )
