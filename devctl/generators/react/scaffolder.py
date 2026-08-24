"""
ReactJS resource scaffolding generator.
Handles the creation of components, hooks, and services.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment


def generate_react_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Scaffolds a React resource (Component, Service).
    """
    env_state = detect_environment(root_path)

    if not env_state["has_react"]:
        typer.secho("❌ Error: No ReactJS project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    react_root = env_state["react_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Structure: src/components/ResourceName/...
    components_dir = os.path.join(react_root, "src", "components", entity_name)
    services_dir = os.path.join(react_root, "src", "services")

    os.makedirs(components_dir, exist_ok=True)
    os.makedirs(services_dir, exist_ok=True)

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"⚙️  Generating ReactJS resource '{entity_name}'...", fg=typer.colors.CYAN)

    context = {
        "entity_name": entity_name,
        "resource_lower": resource_lower,
        "fields_str": fields_str,
    }

    # 1. Generate Component (tsx)
    component_content = env.get_template("component.tsx.j2").render(**context)
    with open(os.path.join(components_dir, f"{entity_name}.tsx"), "w", encoding="utf-8") as f:
        f.write(component_content)

    # 2. Generate Service
    service_content = env.get_template("service.ts.j2").render(**context)
    service_path = os.path.join(services_dir, f"{resource_lower}.service.ts")
    with open(service_path, "w", encoding="utf-8") as f:
        f.write(service_content)

    typer.secho(f"✅ {entity_name} React feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: src/components/{entity_name}/{entity_name}.tsx")
    typer.echo(f"  - Created: src/services/{resource_lower}.service.ts")
