"""
Go (Fiber) resource scaffolding generator.
Handles the creation of handlers and models.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment


def generate_go_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Scaffolds a Go resource.
    """
    env_state = detect_environment(root_path)

    if not env_state["has_go"]:
        typer.secho("❌ Error: No Go project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    go_root = env_state["go_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Structure: handlers/resource.go, models/resource.go
    handlers_dir = os.path.join(go_root, "handlers")
    models_dir = os.path.join(go_root, "models")

    os.makedirs(handlers_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"⚙️  Generating Go resource '{entity_name}'...", fg=typer.colors.CYAN)

    context = {
        "entity_name": entity_name,
        "resource_lower": resource_lower,
        "fields_str": fields_str,
    }

    # 1. Generate Model
    model_content = env.get_template("model.go.j2").render(**context)
    with open(os.path.join(models_dir, f"{resource_lower}.go"), "w", encoding="utf-8") as f:
        f.write(model_content)

    # 2. Generate Handler
    handler_content = env.get_template("handler.go.j2").render(**context)
    with open(os.path.join(handlers_dir, f"{resource_lower}.go"), "w", encoding="utf-8") as f:
        f.write(handler_content)

    typer.secho(f"✅ {entity_name} Go feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: models/{resource_lower}.go")
    typer.echo(f"  - Created: handlers/{resource_lower}.go")
