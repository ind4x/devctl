"""
Generators for Svelte projects.
Includes boilerplate generation via create-svelte.
"""

import os
import subprocess

import typer


def generate_svelte_boilerplate(project_name: str) -> bool:
    """
    Generates a new SvelteKit project using create-svelte via npx.
    """
    typer.secho(f"Generating Svelte project '{project_name}'...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")

    try:
        typer.secho("Scaffolding SvelteKit project...", fg=typer.colors.CYAN)
        from devctl.utils import get_platform

        platform = get_platform()
        # Using a non-interactive way to scaffold svelte
        # We'll use the 'skeleton' template with TypeScript
        subprocess.run(
            [
                "npx",
                "sv",
                "create",
                safe_name,
                "--template",
                "minimal",
                "--types",
                "ts",
                "--no-add-ons",
                "--no-install",
            ],
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

        typer.secho(f"Svelte project '{safe_name}' successfully generated!", fg=typer.colors.GREEN)
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(f"Error: Svelte creation failed with code: {e.returncode}", fg=typer.colors.RED)
        return False
    except Exception as e:
        typer.secho(f"Error: Svelte initialization failed: {e}", fg=typer.colors.RED)
        return False
