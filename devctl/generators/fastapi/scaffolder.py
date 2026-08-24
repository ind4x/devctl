"""
FastAPI resource scaffolding generator.
Handles the creation of routers, schemas, and models.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment


def generate_fastapi_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Scaffolds a FastAPI resource.
    """
    env_state = detect_environment(root_path)

    if not env_state["has_fastapi"]:
        typer.secho("❌ Error: No FastAPI project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    fastapi_root = env_state["fastapi_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Create directories
    routers_dir = os.path.join(fastapi_root, "routers")
    schemas_dir = os.path.join(fastapi_root, "schemas")
    models_dir = os.path.join(fastapi_root, "models")

    for d in [routers_dir, schemas_dir, models_dir]:
        os.makedirs(d, exist_ok=True)
        # Ensure __init__.py exists
        with open(os.path.join(d, "__init__.py"), "a"):
            pass

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"⚙️  Generating FastAPI resource '{entity_name}'...", fg=typer.colors.CYAN)

    context = {
        "entity_name": entity_name,
        "resource_lower": resource_lower,
        "fields_str": fields_str,
    }

    # 1. Generate Schema (Pydantic)
    schema_content = env.get_template("schema.py.j2").render(**context)
    with open(os.path.join(schemas_dir, f"{resource_lower}.py"), "w", encoding="utf-8") as f:
        f.write(schema_content)

    # 2. Generate Router
    router_content = env.get_template("router.py.j2").render(**context)
    with open(os.path.join(routers_dir, f"{resource_lower}.py"), "w", encoding="utf-8") as f:
        f.write(router_content)

    typer.secho(f"{entity_name} FastAPI feature successfully generated!", fg=typer.colors.GREEN)
    typer.echo(f"  - Created: schemas/{resource_lower}.py")
    typer.echo(f"  - Created: routers/{resource_lower}.py")
