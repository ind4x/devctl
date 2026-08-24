"""
Generators for Django projects.
Includes boilerplate generation with Django and DRF.
"""

import os
import subprocess
import sys

import typer
from jinja2 import Environment, FileSystemLoader


def generate_django_boilerplate(project_name: str) -> bool:
    """
    Generates a new Django project.
    """
    typer.secho(f"Generating Django project '{project_name}'...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("-", "_")  # Django prefers underscores
    project_path = os.path.join(os.getcwd(), project_name)

    try:
        os.makedirs(project_path, exist_ok=True)

        templates_dir = os.path.join(os.path.dirname(__file__), "templates", "config")
        env = Environment(loader=FileSystemLoader(templates_dir))

        # 1. Create requirements.txt
        req_content = env.get_template("requirements.txt.j2").render()
        with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write(req_content)

        python_exe = "python" if sys.platform == "win32" else "python3"

        # 2. Create virtual environment
        typer.secho("Creating virtual environment...", fg=typer.colors.CYAN)
        subprocess.run(
            [python_exe, "-m", "venv", ".venv"],
            cwd=project_path,
            check=True,
            shell=(sys.platform == "win32"),
        )

        # 3. Install Django
        typer.secho("Installing Django and DRF...", fg=typer.colors.CYAN)
        if sys.platform == "win32":
            pip_path = os.path.join(".venv", "Scripts", "pip.exe")
        else:
            pip_path = os.path.join(".venv", "bin", "pip")
        subprocess.run(
            [pip_path, "install", "django", "djangorestframework"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=(sys.platform == "win32"),
        )

        # 4. Start Project
        typer.secho("Scaffolding Django project structure...", fg=typer.colors.CYAN)
        if sys.platform == "win32":
            django_admin = os.path.join(".venv", "Scripts", "django-admin.exe")
        else:
            django_admin = os.path.join(".venv", "bin", "django-admin")
        subprocess.run(
            [django_admin, "startproject", safe_name, "."],
            cwd=project_path,
            check=True,
            shell=(sys.platform == "win32"),
        )

        # 5. Create core app
        if sys.platform == "win32":
            python_path = os.path.join(".venv", "Scripts", "python.exe")
        else:
            python_path = os.path.join(".venv", "bin", "python")
        subprocess.run(
            [python_path, "manage.py", "startapp", "core"],
            cwd=project_path,
            check=True,
            shell=(sys.platform == "win32"),
        )

        typer.secho(
            f"Django project '{project_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except Exception as e:
        typer.secho(f"Error: Django initialization failed: {e}", fg=typer.colors.RED)
        return False
