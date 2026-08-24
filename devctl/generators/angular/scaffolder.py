"""
Angular resource scaffolding generator.
Handles the creation of features including models, services, and components.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

from devctl.orchestrator.scanner import detect_environment

# Dictionary mapping CLI types to TypeScript types
TS_TYPE_MAP = {
    "string": "string",
    "int": "number",
    "integer": "number",
    "double": "number",
    "float": "number",
    "boolean": "boolean",
    "date": "string",  # In JSON, dates are typically transmitted as ISO strings
}


def parse_ts_fields(fields_str: str):
    """Transforms terminal fields into TypeScript types."""
    if not fields_str:
        return []
    parsed = []
    for raw in [f.strip() for f in fields_str.split(",") if f.strip()]:
        if ":" not in raw:
            continue
        name, field_type = raw.split(":", 1)
        ts_type = TS_TYPE_MAP.get(field_type.lower().strip(), "string")
        parsed.append({"name": name.strip(), "ts_type": ts_type})
    return parsed


def generate_angular_resource(resource_name: str, fields_str: str, root_path: str = "."):
    """
    Orchestrates the creation of a complete Angular feature.
    """
    env_state = detect_environment(root_path)

    if not env_state["has_angular"]:
        typer.secho("Error: No Angular project detected here.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    angular_root = env_state["angular_path"]
    resource_lower = resource_name.lower()
    entity_name = resource_name.capitalize()

    # Feature target directory: src/app/features/resource_name
    feature_dir = os.path.join(angular_root, "src", "app", "features", resource_lower)

    # Components to generate
    components = [
        # Models
        {
            "dir": "models",
            "suffix": "-request.model",
            "ext": ".ts",
            "template": "models/request.model.ts.j2",
        },
        {
            "dir": "models",
            "suffix": "-response.model",
            "ext": ".ts",
            "template": "models/response.model.ts.j2",
        },
        # Service
        {
            "dir": "services",
            "suffix": ".service",
            "ext": ".ts",
            "template": "services/service.ts.j2",
        },
        # Routes (at feature root)
        {"dir": "", "suffix": ".routes", "ext": ".ts", "template": "routes.ts.j2"},
        # List Component
        {
            "dir": f"pages/{resource_lower}-list",
            "suffix": "-list.component",
            "ext": ".ts",
            "template": "pages/list/list.component.ts.j2",
        },
        {
            "dir": f"pages/{resource_lower}-list",
            "suffix": "-list.component",
            "ext": ".html",
            "template": "pages/list/list.component.html.j2",
        },
        {
            "dir": f"pages/{resource_lower}-list",
            "suffix": "-list.component",
            "ext": ".scss",
            "template": "pages/list/list.component.scss.j2",
        },
        # Form Component
        {
            "dir": f"pages/{resource_lower}-form",
            "suffix": "-form.component",
            "ext": ".ts",
            "template": "pages/form/form.component.ts.j2",
        },
        {
            "dir": f"pages/{resource_lower}-form",
            "suffix": "-form.component",
            "ext": ".html",
            "template": "pages/form/form.component.html.j2",
        },
        {
            "dir": f"pages/{resource_lower}-form",
            "suffix": "-form.component",
            "ext": ".scss",
            "template": "pages/form/form.component.scss.j2",
        },
    ]

    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "feature")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(f"Generating Angular feature '{entity_name}'...", fg=typer.colors.CYAN)

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

        target_file_name = f"{resource_lower}{comp['suffix']}{comp['ext']}"

        try:
            template = env.get_template(comp["template"])
            content = template.render(context)

            with open(os.path.join(target_dir, target_file_name), "w", encoding="utf-8") as f:
                f.write(content)

            display_dir = comp["dir"] if comp["dir"] else "feature root"
            typer.echo(f"  - Created: {display_dir}/{target_file_name}")

        except Exception as e:
            # Tip: if no .scss.j2 template exists, create an empty file automatically
            if comp["ext"] == ".scss":
                with open(os.path.join(target_dir, target_file_name), "w") as f:
                    f.write("")
                typer.echo(f"  - Created (empty): {comp['dir']}/{target_file_name}")
            else:
                typer.secho(
                    f"Warning: Failed to generate {comp['template']}: {e}",
                    fg=typer.colors.YELLOW,
                )

    typer.secho(f"{entity_name} feature successfully generated!", fg=typer.colors.GREEN)
