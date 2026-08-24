"""
CLI command group for initializing new projects.
Supports Spring Boot, Angular, Vue.js, NestJS, NodeJS, React, NextJS, FastAPI,
Django, Svelte, and Go.
"""

import typer

from devctl.generators.angular import generate_angular_boilerplate
from devctl.generators.django import generate_django_boilerplate
from devctl.generators.fastapi import generate_fastapi_boilerplate
from devctl.generators.go_fiber import generate_go_boilerplate
from devctl.generators.nestjs import generate_nest_boilerplate
from devctl.generators.nextjs import generate_nextjs_boilerplate
from devctl.generators.nodejs import generate_nodejs_boilerplate
from devctl.generators.react import generate_react_boilerplate
from devctl.generators.spring import download_spring_boilerplate
from devctl.generators.svelte import generate_svelte_boilerplate
from devctl.generators.vue import generate_vue_boilerplate
from devctl.orchestrator.config_builder import generate_config
from devctl.utils.dependencies import check_tool

# Local Typer application for "init" command group
app = typer.Typer(help="Initializes a new project based on the chosen framework.")


@app.command("spring")
def init_spring(
    name: str,
    db: str = typer.Option("postgres", help="Database type (postgres, mysql, or mongodb)"),
    port: int = typer.Option(None, help="Local port (optional)"),
):
    """
    Initializes a new Spring Boot backend project with its database.
    """
    check_tool("java", "initializing a Spring Boot project")

    # Strict input validation
    if db not in ["postgres", "mysql", "mongodb"]:
        typer.secho(f"Error: Database '{db}' is not supported.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Initializing Spring Boot project: '{name}'...", fg=typer.colors.CYAN)

    success_download = download_spring_boilerplate(name, db_type=db)

    if success_download:
        generate_config(name, db_type=db, custom_port=port)
        typer.secho("\nSpring project ready!", fg=typer.colors.GREEN)


@app.command("angular")
def init_angular(name: str):
    """
    Initializes a new Angular frontend project.
    """
    check_tool("npm", "initializing an Angular project")
    check_tool("ng", "initializing an Angular project")

    typer.secho(f"Initializing Angular project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_angular_boilerplate(name)

    if success:
        typer.secho("\nAngular project ready!", fg=typer.colors.GREEN)


@app.command("vue")
def init_vue(name: str):
    """
    Initializes a new Vue.js frontend project (Vite + TS).
    """
    check_tool("npm", "initializing a Vue.js project")

    typer.secho(f"Initializing Vue.js project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_vue_boilerplate(name)

    if success:
        typer.secho("\nVue.js project ready!", fg=typer.colors.GREEN)


@app.command("nest")
def init_nest(name: str):
    """
    Initializes a new NestJS backend project.
    """
    check_tool("npm", "initializing a NestJS project")

    typer.secho(f"Initializing NestJS project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_nest_boilerplate(name)

    if success:
        typer.secho("\nNestJS project ready!", fg=typer.colors.GREEN)


@app.command("nodejs")
def init_nodejs(name: str):
    """
    Initializes a new NodeJS/Express backend project.
    """
    check_tool("npm", "initializing a NodeJS project")

    typer.secho(f"Initializing NodeJS project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_nodejs_boilerplate(name)

    if success:
        typer.secho("\nNodeJS project ready!", fg=typer.colors.GREEN)


@app.command("react")
def init_react(name: str):
    """
    Initializes a new ReactJS frontend project (Vite + TS).
    """
    check_tool("npm", "initializing a ReactJS project")

    typer.secho(f"Initializing ReactJS project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_react_boilerplate(name)

    if success:
        typer.secho("\nReactJS project ready!", fg=typer.colors.GREEN)


@app.command("nextjs")
def init_nextjs(name: str):
    """
    Initializes a new NextJS frontend project.
    """
    check_tool("npm", "initializing a NextJS project")

    typer.secho(f"Initializing NextJS project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_nextjs_boilerplate(name)

    if success:
        typer.secho("\nNextJS project ready!", fg=typer.colors.GREEN)


@app.command("fastapi")
def init_fastapi(name: str):
    """
    Initializes a new FastAPI backend project.
    """
    check_tool("python3", "initializing a FastAPI project")

    typer.secho(f"Initializing FastAPI project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_fastapi_boilerplate(name)

    if success:
        typer.secho("\nFastAPI project ready!", fg=typer.colors.GREEN)


@app.command("django")
def init_django(name: str):
    """
    Initializes a new Django backend project.
    """
    check_tool("python3", "initializing a Django project")

    typer.secho(f"Initializing Django project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_django_boilerplate(name)

    if success:
        typer.secho("\nDjango project ready!", fg=typer.colors.GREEN)


@app.command("svelte")
def init_svelte(name: str):
    """
    Initializes a new SvelteKit frontend project.
    """
    check_tool("npm", "initializing a Svelte project")

    typer.secho(f"Initializing Svelte project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_svelte_boilerplate(name)

    if success:
        typer.secho("\nSvelte project ready!", fg=typer.colors.GREEN)


@app.command("go")
def init_go(name: str):
    """
    Initializes a new Go/Fiber backend project.
    """
    check_tool("go", "initializing a Go project")

    typer.secho(f"Initializing Go project: '{name}'...", fg=typer.colors.CYAN)
    success = generate_go_boilerplate(name)

    if success:
        typer.secho("\nGo project ready!", fg=typer.colors.GREEN)
