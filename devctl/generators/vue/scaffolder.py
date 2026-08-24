"""
Vue.js resource scaffolding generator.
Handles the creation of features including models, services, and views.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape

from devctl.generators.angular.scaffolder import parse_ts_fields
from devctl.orchestrator.scanner import detect_environment


def generate_vue_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Orchestrates the creation of a complete Vue 3 feature.
    """
    env_state = detect_environment(root_path)

    if not env_state["has_vue"]:
        typer.secho("Error: No Vue.js project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    vue_root = env_state["vue_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Feature target directory: src/features/resource_name
    feature_dir = os.path.join(vue_root, "src", "features", resource_lower)

    # Subdirectories and files to generate
    components = [
        # Models
        {
            "dir": "models",
            "suffix": "Models",
            "ext": ".ts",
            "template": "models.ts.j2",
        },
        # Service
        {
            "dir": "services",
            "suffix": "Service",
            "ext": ".ts",
            "template": "service.ts.j2",
        },
        # Routes
        {
            "dir": "",
            "suffix": "Routes",
            "ext": ".ts",
            "template": "routes.ts.j2",
        },
        # List Component
        {
            "dir": "views",
            "suffix": "List",
            "ext": ".vue",
            "template": "List.vue.j2",
        },
        # Form Component
        {
            "dir": "views",
            "suffix": "Form",
            "ext": ".vue",
            "template": "Form.vue.j2",
        },
    ]

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "feature")
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    typer.secho(f"Generating Vue.js feature '{entity_name}'...", fg=typer.colors.CYAN)

    # Template data
    context = {
        "entity_name": entity_name,
        "resource_name_lower": resource_lower,
        "table_name": f"{resource_lower}s",
        "uppercase_name": resource_name.upper(),
        "fields": parse_ts_fields(fields_str),
    }

    for comp in components:
        # Create target directory
        target_dir = os.path.join(feature_dir, os.path.normpath(comp["dir"]))
        os.makedirs(target_dir, exist_ok=True)

        target_file_name = f"{entity_name}{comp['suffix']}{comp['ext']}"
        # Adjust name for routes to be lowercase e.g. taskRoutes.ts
        if comp["suffix"] == "Routes":
            target_file_name = f"{resource_lower}{comp['suffix']}{comp['ext']}"

        try:
            template = env.get_template(comp["template"])
            content = template.render(context)

            with open(os.path.join(target_dir, target_file_name), "w", encoding="utf-8") as f:
                f.write(content)

            display_dir = comp["dir"] if comp["dir"] else "feature root"
            typer.echo(f"  - Created: {display_dir}/{target_file_name}")

        except Exception as e:
            typer.secho(f"Warning: Error on {comp['template']}: {e}", fg=typer.colors.YELLOW)

    typer.secho(f"{entity_name} Vue feature successfully generated!", fg=typer.colors.GREEN)
