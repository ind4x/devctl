"""
Generators for NextJS projects.
Includes boilerplate generation via create-next-app.
"""

import subprocess

import typer


def generate_nextjs_boilerplate(project_name: str) -> bool:
    """
    Generates a new NextJS project using create-next-app via npx.
    """
    typer.secho(f"🔄 Generating NextJS project '{project_name}'...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")

    try:
        typer.secho("Scaffolding NextJS project (this may take a minute)...", fg=typer.colors.CYAN)
        # --ts: TypeScript
        # --eslint: ESLint
        # --tailwind: Tailwind CSS
        # --src-dir: Use src/ directory
        # --app: Use App Router
        # --import-alias: alias for imports
        from devctl.utils import get_platform
        platform = get_platform()
        subprocess.run(
            [
                "npx",
                "create-next-app@latest",
                safe_name,
                "--ts",
                "--eslint",
                "--tailwind",
                "--src-dir",
                "--app",
                "--import-alias",
                "@/*",
                "--use-npm",
            ],
            check=True,
            shell=platform.shell_required,
        )

        typer.secho(
            f"✅ NextJS project '{safe_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(f"❌ NextJS creation failed with code: {e.returncode}", fg=typer.colors.RED)
        return False
    except Exception as e:
        typer.secho(f"❌ NextJS initialization failed: {e}", fg=typer.colors.RED)
        return False
