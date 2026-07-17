"""
Generators for NestJS projects.
Includes boilerplate generation via Nest CLI.
"""

import subprocess

import typer


def generate_nest_boilerplate(project_name: str) -> bool:
    """
    Generates a new NestJS project using the Nest CLI via npx.
    """
    typer.secho(f"🔄 Generating NestJS project '{project_name}'...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")

    try:
        # Use npx to run Nest CLI without requiring global installation
        # --package-manager npm: ensures npm is used
        # --strict: enables strict mode
        # --skip-git: devctl might be in a git repo already
        typer.secho("Scaffolding NestJS project (this may take a minute)...", fg=typer.colors.CYAN)
        from devctl.utils import get_platform

        platform = get_platform()
        subprocess.run(
            [
                "npx",
                "-p",
                "@nestjs/cli",
                "nest",
                "new",
                safe_name,
                "--package-manager",
                "npm",
                "--skip-git",
            ],
            check=True,
            shell=platform.shell_required,
        )

        typer.secho(
            f"✅ NestJS project '{safe_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(f"❌ Nest CLI process failed with code: {e.returncode}", fg=typer.colors.RED)
        return False
    except FileNotFoundError:
        typer.secho("❌ Error: 'npx' or 'npm' not found in path.", fg=typer.colors.RED)
        return False
