"""
Svelte resource scaffolding generator.
Handles the creation of components and routes.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment


def generate_svelte_resource(resource_name: str, _fields_str: str, root_path: str = "."):
    """
    Scaffolds a Svelte resource (Route, Component).
    """
    env_state = detect_environment(root_path)

    if not env_state["has_svelte"]:
        typer.secho("❌ Error: No Svelte project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    svelte_root = env_state["svelte_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Structure: src/routes/resource-name/+page.svelte
    routes_dir = os.path.join(svelte_root, "src", "routes", resource_lower)
    components_dir = os.path.join(svelte_root, "src", "lib", "components")

    os.makedirs(routes_dir, exist_ok=True)
    os.makedirs(components_dir, exist_ok=True)

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"⚙️  Generating Svelte resource '{entity_name}'...", fg=typer.colors.CYAN)

    context = {
        "entity_name": entity_name,
        "resource_lower": resource_lower,
    }

    # 1. Generate +page.svelte
    page_content = env.get_template("page.svelte.j2").render(**context)
    with open(os.path.join(routes_dir, "+page.svelte"), "w", encoding="utf-8") as f:
        f.write(page_content)

    # 2. Generate Component
    component_content = env.get_template("component.svelte.j2").render(**context)
    comp_path = os.path.join(components_dir, f"{entity_name}List.svelte")
    with open(comp_path, "w", encoding="utf-8") as f:
        f.write(component_content)

    typer.secho(f"✅ {entity_name} Svelte feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: src/routes/{resource_lower}/+page.svelte")
    typer.echo(f"  - Created: src/lib/components/{entity_name}List.svelte")
