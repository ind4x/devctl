"""
NodeJS/Express resource scaffolding generator.
Handles the creation of routes and controllers.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment


def generate_nodejs_resource(resource_name: str, _fields_str: str, root_path: str = "."):
    """
    Scaffolds a NodeJS/Express resource.
    """
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    src_dir = os.path.join(root_path, "src")
    if not os.path.exists(src_dir):
        # Try to find nodejs path from scanner
        detect_environment(root_path)
        src_dir = os.path.join(root_path, "src")

    routes_dir = os.path.join(src_dir, "routes")
    controllers_dir = os.path.join(src_dir, "controllers")

    os.makedirs(routes_dir, exist_ok=True)
    os.makedirs(controllers_dir, exist_ok=True)

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"⚙️  Generating NodeJS/Express resource '{entity_name}'...", fg=typer.colors.CYAN)

    context = {
        "entity_name": entity_name,
        "resource_lower": resource_lower,
    }

    # 1. Generate Controller
    controller_content = env.get_template("controller.ts.j2").render(**context)
    controller_path = os.path.join(controllers_dir, f"{resource_lower}.controller.ts")
    with open(controller_path, "w", encoding="utf-8") as f:
        f.write(controller_content)

    # 2. Generate Route
    route_content = env.get_template("routes.ts.j2").render(**context)
    route_path = os.path.join(routes_dir, f"{resource_lower}.routes.ts")
    with open(route_path, "w", encoding="utf-8") as f:
        f.write(route_content)

    typer.secho(f"✅ {entity_name} NodeJS resource successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: controllers/{resource_lower}.controller.ts")
    typer.echo(f"  - Created: routes/{resource_lower}.routes.ts")
    typer.echo("💡 Don't forget to register the route in your main app file.")
