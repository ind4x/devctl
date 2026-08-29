"""
Configuration builder for Spring Boot projects.
Generates docker-compose-db.yml and application.properties with dynamic database settings.
"""

import os

import typer
from jinja2 import Environment, FileSystemLoader


def generate_config(project_name: str, db_type: str = "postgres", custom_port: int = None):
    """
    Generates the initial configuration (Docker and Spring properties) for a new project.
    """
    template_dir = os.path.join(
        os.path.dirname(__file__), "..", "generators", "spring", "templates"
    )
    env = Environment(loader=FileSystemLoader(template_dir))

    # Intelligent default port resolution
    if custom_port is None:
        if db_type == "postgres":
            db_port = 5432
        elif db_type == "mysql":
            db_port = 3306
        elif db_type == "mongodb":
            db_port = 27017
        else:
            db_port = 5432
    else:
        db_port = custom_port

    context = {
        "project_name": project_name,
        "db_type": db_type,
        "db_service_name": f"{project_name}-db",
        "db_name": f"{project_name}_db".replace("-", "_"),
        "db_user": "admin",
        "db_password": "password",
        "db_port": db_port,
    }

    project_path = os.path.join(os.getcwd(), project_name)

    try:
        docker_template = env.get_template("docker-compose.yml.j2")
        with open(os.path.join(project_path, "docker-compose-db.yml"), "w") as f:
            f.write(docker_template.render(context))

        props_path = os.path.join(
            project_path, "src", "main", "resources", "application.properties"
        )
        if os.path.exists(props_path):
            props_template = env.get_template("application.properties.j2")
            with open(props_path, "w") as f:
                f.write(props_template.render(context))

        typer.secho(
            f"Dynamic configuration ({db_type} on port {db_port}) generated.",
            fg=typer.colors.GREEN,
        )
        return True
    except Exception as e:
        typer.secho(f"Error: Configuration failed: {e}", fg=typer.colors.RED)
        return False
