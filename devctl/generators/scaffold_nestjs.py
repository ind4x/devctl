"""
NestJS resource scaffolding generator.
Handles the creation of modules, controllers, and services using Nest CLI.
"""

import subprocess

import typer

from devctl.orchestrator.scanner import detect_environment


def generate_nest_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Scaffolds a NestJS resource using the Nest CLI.
    """
    env_state = detect_environment(root_path)

    if not env_state["has_nest"]:
        typer.secho("❌ Error: No NestJS project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    nest_root = env_state["nest_path"]
    resource_lower = resource_name.lower()

    typer.secho(f"⚙️  Generating NestJS resource '{resource_name}'...", fg=typer.colors.CYAN)

    from devctl.utils import get_platform
    platform = get_platform()
    try:
        # Use npx to run Nest CLI
        # 'g res' is shorthand for 'generate resource'
        # --no-spec skips test files for a cleaner scaffold
        subprocess.run(
            ["npx", "@nestjs/cli", "g", "resource", resource_lower, "--no-spec"],
            cwd=nest_root,
            check=True,
            shell=platform.shell_required,
        )

        typer.secho(
            f"✅ {resource_name} NestJS resource successfully generated!", fg=typer.colors.GREEN
        )
        typer.echo(
            f"💡 Note: Fields [{fields_str}] were provided but manual DTO update "
            "is recommended for NestJS."
        )

    except subprocess.CalledProcessError as e:
        typer.secho(
            f"❌ Nest CLI resource generation failed with code: {e.returncode}",
            fg=typer.colors.RED,
        )
    except Exception as e:
        typer.secho(f"⚠️  An unexpected error occurred: {e}", fg=typer.colors.YELLOW)
