"""
NextJS resource scaffolding generator.
Handles the creation of pages and components in the App Router.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment


def generate_nextjs_resource(resource_name: str, _fields_str: str, root_path: str = "."):
    """
    Scaffolds a NextJS resource (Page, Component).
    """
    env_state = detect_environment(root_path)

    if not env_state["has_nextjs"]:
        typer.secho("❌ Error: No NextJS project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    nextjs_root = env_state["nextjs_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Structure: src/app/resource-name/page.tsx
    app_dir = os.path.join(nextjs_root, "src", "app", resource_lower)
    components_dir = os.path.join(nextjs_root, "src", "components")

    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(components_dir, exist_ok=True)

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"⚙️  Generating NextJS resource '{entity_name}'...", fg=typer.colors.CYAN)

    context = {
        "entity_name": entity_name,
        "resource_lower": resource_lower,
    }

    # 1. Generate Page (tsx)
    page_content = env.get_template("page.tsx.j2").render(**context)
    with open(os.path.join(app_dir, "page.tsx"), "w", encoding="utf-8") as f:
        f.write(page_content)

    # 2. Generate Component
    component_content = env.get_template("component.tsx.j2").render(**context)
    with open(os.path.join(components_dir, f"{entity_name}List.tsx"), "w", encoding="utf-8") as f:
        f.write(component_content)

    typer.secho(f"✅ {entity_name} NextJS feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: src/app/{resource_lower}/page.tsx")
    typer.echo(f"  - Created: src/components/{entity_name}List.tsx")
