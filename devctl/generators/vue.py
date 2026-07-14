"""
Generators for Vue.js projects via Vite.
Includes boilerplate generation, proxy setup, and router configuration.
"""

import os
import subprocess

import typer
from jinja2 import Environment, FileSystemLoader


def setup_vue_proxy(project_path: str):
    """
    Replaces the default vite.config.ts with our version including the proxy.
    """
    typer.secho("Configuring Vite Proxy for Spring Boot...", fg=typer.colors.CYAN)

    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "vue", "config")
    env = Environment(loader=FileSystemLoader(templates_dir))

    target_path = os.path.join(project_path, "vite.config.ts")

    try:
        template = env.get_template("vite.config.ts.j2")
        content = template.render()
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        typer.echo("  - vite.config.ts updated with /api proxy.")
    except Exception as e:
        typer.secho(f"Warning: Error configuring proxy: {e}", fg=typer.colors.YELLOW)


def setup_vue_router(project_path: str):
    """
    Installs vue-router and configures the base architecture (main.ts, router, App.vue).
    """
    typer.secho("Installing and configuring vue-router...", fg=typer.colors.CYAN)

    from devctl.utils import get_platform
    platform = get_platform()
    try:
        # 1. NPM package installation
        subprocess.run(
            ["npm", "install", "vue-router@4"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=platform.shell_required,
        )

        # 2. Router directory creation
        src_dir = os.path.join(project_path, "src")
        router_dir = os.path.join(src_dir, "router")
        os.makedirs(router_dir, exist_ok=True)

        # 3. Jinja2 template rendering
        templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "vue", "config")
        env = Environment(loader=FileSystemLoader(templates_dir))

        files_to_generate = {
            "router.ts.j2": os.path.join(router_dir, "index.ts"),
            "main.ts.j2": os.path.join(src_dir, "main.ts"),
            "App.vue.j2": os.path.join(src_dir, "App.vue"),
        }

        for tpl_name, target_path in files_to_generate.items():
            template = env.get_template(tpl_name)
            content = template.render()
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

        typer.echo("  - Navigation architecture ready.")
    except Exception as e:
        typer.secho(f"Warning: Error configuring router: {e}", fg=typer.colors.YELLOW)


def generate_vue_boilerplate(project_name: str) -> bool:
    """
    Generates a Vue 3 + TypeScript project via Vite.
    """
    typer.secho(f"Generating Vue.js frontend '{project_name}' via Vite...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")

    from devctl.utils import get_platform
    platform = get_platform()
    try:
        typer.secho("Scaffolding Vite project...", fg=typer.colors.CYAN)
        subprocess.run(
            ["npm", "create", "vite@latest", safe_name, "--", "--template", "vue-ts"],
            check=True,
            shell=platform.shell_required,
        )

        project_full_path = os.path.join(os.getcwd(), safe_name)

        typer.secho("Installing npm dependencies...", fg=typer.colors.CYAN)
        subprocess.run(
            ["npm", "install"],
            cwd=project_full_path,
            check=True,
            shell=platform.shell_required,
        )

        # --- CALL OUR TWO CONFIGURATORS ---
        setup_vue_proxy(project_full_path)
        setup_vue_router(project_full_path)
        # ----------------------------------------

        typer.secho(f"Vue.js frontend '{safe_name}' successfully generated!", fg=typer.colors.GREEN)
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(
            f"Error: Vue/Vite process failed with code: {e.returncode}", fg=typer.colors.RED
        )
        return False
