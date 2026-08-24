"""
Django resource scaffolding generator.
Handles the creation of models, serializers, and views.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment


def generate_django_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Scaffolds a Django resource.
    """
    env_state = detect_environment(root_path)

    if not env_state["has_django"]:
        typer.secho("❌ Error: No Django project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    django_root = env_state["django_path"]
    resource_name.lower()
    entity_name = resource_name.capitalize()

    # Structure: core/models.py, core/serializers.py, core/views.py
    # For simplicity, we inject into the 'core' app created during init
    core_dir = os.path.join(django_root, "core")
    if not os.path.exists(core_dir):
        os.makedirs(core_dir, exist_ok=True)

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"⚙️  Generating Django resource '{entity_name}'...", fg=typer.colors.CYAN)

    context = {
        "entity_name": entity_name,
        "fields_str": fields_str,
    }

    # 1. Append Model
    model_snippet = "\n" + env.get_template("model.py.j2").render(**context) + "\n"
    with open(os.path.join(core_dir, "models.py"), "a", encoding="utf-8") as f:
        f.write(model_snippet)

    # 2. Append Serializer
    serializer_path = os.path.join(core_dir, "serializers.py")
    if not os.path.exists(serializer_path):
        with open(serializer_path, "w", encoding="utf-8") as f:
            f.write("from rest_framework import serializers\nfrom .models import *\n")

    serializer_snippet = "\n" + env.get_template("serializer.py.j2").render(**context) + "\n"
    with open(serializer_path, "a", encoding="utf-8") as f:
        f.write(serializer_snippet)

    # 3. Append View
    view_snippet = "\n" + env.get_template("view.py.j2").render(**context) + "\n"
    with open(os.path.join(core_dir, "views.py"), "a", encoding="utf-8") as f:
        f.write(view_snippet)

    typer.secho(f"✅ {entity_name} Django feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo("  - Updated: core/models.py")
    typer.echo("  - Updated: core/serializers.py")
    typer.echo("  - Updated: core/views.py")
