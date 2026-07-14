"""
Generators for ReactJS projects via Vite.
Includes boilerplate generation and basic configuration.
"""

import os
import subprocess

import typer


def generate_react_boilerplate(project_name: str) -> bool:
    """
    Generates a new React + TypeScript project via Vite.
    """
    typer.secho(f"Generating ReactJS frontend '{project_name}' via Vite...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")

    try:
        from devctl.utils import get_platform
        platform = get_platform()
        typer.secho("Scaffolding React project...", fg=typer.colors.CYAN)
        subprocess.run(
            ["npm", "create", "vite@latest", safe_name, "--", "--template", "react-ts"],
            check=True,
            shell=platform.shell_required,
        )

        project_full_path = os.path.join(os.getcwd(), safe_name)

        typer.secho("Installing npm dependencies...", fg=typer.colors.CYAN)
        subprocess.run(
            ["npm", "install"],
            cwd=project_full_path,
            check=True,
            shell=platform.shell_required,
        )

        typer.secho(
            f"ReactJS frontend '{safe_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(
            f"Error: React/Vite process failed with code: {e.returncode}", fg=typer.colors.RED
        )
        return False
    except Exception as e:
        typer.secho(f"Error: React/Vite initialization failed: {e}", fg=typer.colors.RED)
        return False
