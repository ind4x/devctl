"""
Spring Boot resource scaffolding generator.
Handles the creation of MVC components, DTOs, Mappers, and Security configuration.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader

# Dictionary mapping CLI types to Java types
JAVA_TYPE_MAP = {
    "string": "String",
    "int": "Integer",
    "integer": "Integer",
    "double": "Double",
    "float": "Float",
    "boolean": "Boolean",
    "date": "LocalDate",
}


def parse_fields(fields_str: str):
    """
    Transforms terminal field strings into injectable data.
    Example: "name:string, age:int" -> [{"name": "name", "java_type": "String"}, ...]
    """
    if not fields_str:
        return []

    parsed_fields = []
    raw_fields = [f.strip() for f in fields_str.split(",") if f.strip()]

    for raw in raw_fields:
        if ":" not in raw:
            continue
        name, field_type = raw.split(":", 1)
        java_type = JAVA_TYPE_MAP.get(field_type.lower().strip(), "String")
        parsed_fields.append({"name": name.strip(), "java_type": java_type})
    return parsed_fields


def find_spring_base_package_and_path():
    """
    Searches for the directory containing the @SpringBootApplication class.
    This is the most reliable way to find the base package without parsing pom.xml.
    """
    java_src_dir = os.path.join(os.getcwd(), "src", "main", "java")

    if not os.path.exists(java_src_dir):
        return None, None

    for root, _dirs, files in os.walk(java_src_dir):
        for file in files:
            if file.endswith("Application.java"):
                rel_path = os.path.relpath(root, java_src_dir)
                base_package = rel_path.replace(os.sep, ".")
                return base_package, root

    return None, None


def generate_spring_resource(resource_name: str, fields_str: str):
    """
    Orchestrates the creation of MVC + DTOs + Mapper architecture.
    """
    base_package, base_path = find_spring_base_package_and_path()

    if not base_package:
        typer.secho(
            "Error: Unable to find a valid Spring Boot project here.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    entity_name = resource_name.capitalize()

    # Detailed configuration for sub-folders (DTOs, Mappers)
    components = [
        {"dir": "entity", "suffix": "Entity", "template": "Entity.java.j2"},
        {"dir": "repository", "suffix": "Repository", "template": "Repository.java.j2"},
        {"dir": "service", "suffix": "Service", "template": "Service.java.j2"},
        {"dir": "service/impl", "suffix": "ServiceImpl", "template": "ServiceImpl.java.j2"},
        {"dir": "controller", "suffix": "Controller", "template": "Controller.java.j2"},
        {"dir": "dto/request", "suffix": "Request", "template": "dto/Request.java.j2"},
        {"dir": "dto/response", "suffix": "Response", "template": "dto/Response.java.j2"},
        {"dir": "mapper", "suffix": "Mapper", "template": "mapper/Mapper.java.j2"},
    ]

    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))

    typer.secho(
        f"Generating Spring resource '{entity_name}' (with MapStruct & DTOs)...",
        fg=typer.colors.CYAN,
    )

    for comp in components:
        class_name = f"{entity_name}{comp['suffix']}"
        target_file_name = f"{class_name}.java"

        # Create sub-folder if it doesn't exist (e.g., src/.../dto/request)
        # os.path.normpath handles OS-specific slashes
        target_dir = os.path.join(base_path, os.path.normpath(comp["dir"]))
        os.makedirs(target_dir, exist_ok=True)

        # Data passed to the Jinja2 template
        context = {
            "base_package": base_package,
            "class_name": class_name,
            "entity_name": entity_name,
            "table_name": f"{resource_name.lower()}s",
            "fields": parse_fields(fields_str),
        }

        template = env.get_template(comp["template"])
        content = template.render(context)

        with open(os.path.join(target_dir, target_file_name), "w", encoding="utf-8") as f:
            f.write(content)

        typer.echo(f"  - Created: {comp['dir']}/{target_file_name}")

    typer.secho(f"{entity_name} architecture successfully generated!", fg=typer.colors.GREEN)


def generate_spring_security(_root_path: str = "."):
    """
    Dynamically generates the JWT security base.
    """
    # Reuse the dynamic detection function
    base_package, base_path = find_spring_base_package_and_path()

    if not base_package:
        typer.secho(
            "Error: Unable to locate Java package for security.",
            fg=typer.colors.RED,
        )
        return

    # Create config folder in the right place
    target_dir = os.path.join(base_path, "config")
    os.makedirs(target_dir, exist_ok=True)

    # Setup Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), "templates", "config")
    env = Environment(loader=FileSystemLoader(templates_dir))

    security_files = [
        "JwtService.java",
        "JwtAuthenticationFilter.java",
        "SecurityConfig.java",
        "ApplicationConfig.java",
    ]

    typer.secho(f"Injecting JWT security into {base_package}.config...", fg=typer.colors.CYAN)

    for filename in security_files:
        template = env.get_template(f"{filename}.j2")
        content = template.render(base_package=base_package)

        with open(os.path.join(target_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        typer.echo(f"  - Created: config/{filename}")

    typer.secho("Security initialized successfully!", fg=typer.colors.GREEN)
