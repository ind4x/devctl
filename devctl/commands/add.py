"""
CLI command group for adding new resources to existing projects.
Supports Spring Boot, Angular, Vue.js, NestJS, NodeJS, React, NextJS, FastAPI,
Django, Svelte, and Go scaffolding.
"""

import os

import typer

from devctl.generators.angular import generate_angular_resource
from devctl.generators.django import generate_django_resource
from devctl.generators.fastapi import generate_fastapi_resource
from devctl.generators.go_fiber import generate_go_resource
from devctl.generators.nestjs import generate_nest_resource
from devctl.generators.nextjs import generate_nextjs_resource
from devctl.generators.nodejs import generate_nodejs_resource
from devctl.generators.react import generate_react_resource
from devctl.generators.spring import generate_spring_resource
from devctl.generators.svelte import generate_svelte_resource
from devctl.generators.vue import generate_vue_resource
from devctl.orchestrator.scanner import detect_environment
from devctl.utils.dependencies import check_tool

app = typer.Typer(help="Adds resources to the current project (Scaffolding).")


@app.command()
def resource(
    name: str = typer.Argument(..., help="The name of the resource (e.g., Client, Product)"),
    fields: str = typer.Option(
        "", "--fields", "-f", help="Fields in the format 'name:type, age:int'"
    ),
):
    """
    Scans the current folder and generates a suitable business architecture.
    """
    typer.secho("Analyzing current context...", fg=typer.colors.CYAN)
    env_state = detect_environment(".")

    original_dir = os.getcwd()
    project_detected = False

    # Check for Spring Boot project
    if env_state["has_spring"]:
        check_tool("java", "generating Spring Boot resources")
        project_detected = True
        typer.secho(
            "Spring Boot project detected. Launching Java generator...", fg=typer.colors.GREEN
        )
        os.chdir(env_state["spring_path"])
        try:
            generate_spring_resource(name, fields)
        except Exception as e:
            typer.secho(f"Error: Spring generation failed: {e}", fg=typer.colors.RED)
        finally:
            os.chdir(original_dir)

    # Check for Angular project
    if env_state["has_angular"]:
        check_tool("npm", "generating Angular resources")
        project_detected = True
        typer.secho(
            "Angular project detected. Launching TypeScript generator...", fg=typer.colors.CYAN
        )
        try:
            generate_angular_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Angular generation failed: {e}", fg=typer.colors.RED)

    # Check for Vue.js project
    if env_state.get("has_vue"):
        check_tool("npm", "generating Vue.js resources")
        project_detected = True
        typer.secho("Vue.js project detected. Launching Vue generator...", fg=typer.colors.GREEN)
        try:
            generate_vue_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Vue generation failed: {e}", fg=typer.colors.RED)

    # Check for NestJS project
    if env_state.get("has_nest"):
        project_detected = True
        typer.secho("NestJS project detected. Launching Nest generator...", fg=typer.colors.CYAN)
        try:
            generate_nest_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Nest generation failed: {e}", fg=typer.colors.RED)

    # Check for React project
    if env_state.get("has_react"):
        project_detected = True
        typer.secho("React project detected. Launching React generator...", fg=typer.colors.BLUE)
        try:
            generate_react_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: React generation failed: {e}", fg=typer.colors.RED)

    # Check for NextJS project
    if env_state.get("has_nextjs"):
        project_detected = True
        typer.secho(
            "NextJS project detected. Launching NextJS generator...", fg=typer.colors.YELLOW
        )
        try:
            generate_nextjs_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: NextJS generation failed: {e}", fg=typer.colors.RED)

    # Check for FastAPI project
    if env_state.get("has_fastapi"):
        project_detected = True
        typer.secho(
            "FastAPI project detected. Launching FastAPI generator...", fg=typer.colors.CYAN
        )
        try:
            generate_fastapi_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: FastAPI generation failed: {e}", fg=typer.colors.RED)

    # Check for Django project
    if env_state.get("has_django"):
        project_detected = True
        typer.secho("Django project detected. Launching Django generator...", fg=typer.colors.GREEN)
        try:
            generate_django_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Django generation failed: {e}", fg=typer.colors.RED)

    # Check for Svelte project
    if env_state.get("has_svelte"):
        project_detected = True
        typer.secho("Svelte project detected. Launching Svelte generator...", fg=typer.colors.RED)
        try:
            generate_svelte_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Svelte generation failed: {e}", fg=typer.colors.RED)

    # Check for Go project
    if env_state.get("has_go"):
        project_detected = True
        typer.secho("Go project detected. Launching Go generator...", fg=typer.colors.CYAN)
        try:
            generate_go_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: Go generation failed: {e}", fg=typer.colors.RED)

    # Check for NodeJS project
    if os.path.exists("package.json") and not project_detected:
        # Heuristic for generic nodejs project if not already caught by others
        project_detected = True
        typer.secho("NodeJS project detected. Launching NodeJS generator...", fg=typer.colors.GREEN)
        try:
            generate_nodejs_resource(name, fields, root_path=".")
        except Exception as e:
            typer.secho(f"Error: NodeJS generation failed: {e}", fg=typer.colors.RED)

    # Error message only if NO project detected
    if not project_detected:
        typer.secho(
            "Error: Unable to determine project type. "
            "Please run from within a supported project directory "
            "(Spring, Angular, React, NextJS, FastAPI, Django, Svelte, Go, or Vue.js).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
