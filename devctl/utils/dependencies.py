"""
Utility functions for checking system dependencies.
Verifies if required tools like Docker, NPM, and Java are installed.
"""

import shutil

import typer


def check_tool(tool_name: str, required_for: str = "this operation"):
    """
    Check if a tool is available in the system PATH.
    If not, print a friendly error message and exit.
    """
    from devctl.utils import get_platform

    platform = get_platform()

    actual_tool = tool_name
    if tool_name == "python3" and platform.python_exe == "python":
        actual_tool = "python"

    if shutil.which(actual_tool) is None:
        if tool_name == "python3" and shutil.which("python") is not None:
            return

        typer.secho(
            f"\nError: '{tool_name}' is not installed or not in your PATH.",
            fg=typer.colors.RED,
            bold=True,
        )
        typer.echo(f"It is required for {required_for}.")

        # Provide helpful hints for common tools
        hints = {
            "docker": "Visit https://docs.docker.com/get-docker/",
            "npm": "Install Node.js from https://nodejs.org/",
            "java": "Install OpenJDK (e.g., version 17) from your package manager.",
            "mvnw": "Ensure you are in a Spring Boot project root with the 'mvnw' wrapper.",
            "ng": "Install Angular CLI using 'npm install -g @angular/cli'.",
        }

        if tool_name in hints:
            typer.echo(f"Hint: {hints[tool_name]}")

        raise typer.Exit(code=1)
