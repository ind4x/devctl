"""
Generators for Angular projects.
Includes boilerplate generation and environment configuration.
"""

import json
import os
import subprocess

import typer
from jinja2 import Environment, FileSystemLoader


def setup_angular_environments(project_path: str):
    """
    Generates environments and proxy for an Angular project.
    """
    typer.secho("Configuring Proxy and Environments...", fg=typer.colors.CYAN)

    # 1. Target paths
    src_dir = os.path.join(project_path, "src")
    env_dir = os.path.join(src_dir, "environments")
    os.makedirs(env_dir, exist_ok=True)

    # 2. Template rendering via Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "angular", "config")
    env = Environment(loader=FileSystemLoader(templates_dir))

    files_to_generate = {
        "proxy.conf.json.j2": os.path.join(project_path, "src", "proxy.conf.json"),
        "environment.ts.j2": os.path.join(env_dir, "environment.ts"),
        "environment.development.ts.j2": os.path.join(env_dir, "environment.development.ts"),
    }

    for tpl_name, target_path in files_to_generate.items():
        try:
            template = env.get_template(tpl_name)
            content = template.render()
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            typer.secho(f"Warning: Failed to generate {tpl_name}: {e}", fg=typer.colors.YELLOW)

    # 3. Modify angular.json to enable the proxy
    angular_json_path = os.path.join(project_path, "angular.json")
    if os.path.exists(angular_json_path):
        with open(angular_json_path, "r", encoding="utf-8") as f:
            angular_config = json.load(f)

        try:
            # Find the default project name (usually the same name as the folder)
            project_name = list(angular_config["projects"].keys())[0]

            # Injection of proxyConfig into the "serve" architect
            serve_target = angular_config["projects"][project_name]["architect"]["serve"]

            # Ensure "options" exists
            if "options" not in serve_target:
                serve_target["options"] = {}

            serve_target["options"]["proxyConfig"] = "src/proxy.conf.json"

            with open(angular_json_path, "w", encoding="utf-8") as f:
                json.dump(angular_config, f, indent=2)

            typer.echo("  - angular.json updated with proxyConfig.")
        except Exception as e:
            typer.secho(
                f"Warning: Unable to modify angular.json automatically: {e}",
                fg=typer.colors.YELLOW,
            )


def generate_angular_boilerplate(project_name: str) -> bool:
    """
    Generates an Angular project via the native CLI (@angular/cli) and configures it.
    """
    typer.secho(f"Generating Angular frontend '{project_name}'...", fg=typer.colors.CYAN)

    safe_name = project_name.lower().replace("_", "-")

    from devctl.utils import get_platform

    platform = get_platform()
    try:
        subprocess.run(
            ["ng", "version"],
            capture_output=True,
            check=True,
            shell=platform.shell_required,
        )
    except FileNotFoundError:
        typer.secho(
            "Error: Angular CLI ('ng') not found on your system.",
            fg=typer.colors.RED,
        )
        return False
    except subprocess.CalledProcessError:
        typer.secho("Error: Angular CLI is installed but not responding.", fg=typer.colors.RED)
        return False

    try:
        command = ["ng", "new", safe_name, "--routing=true", "--style=scss", "--skip-git=true"]

        typer.secho("Downloading npm packages... (This may take 1-2 minutes)", fg=typer.colors.CYAN)
        subprocess.run(command, check=True, shell=platform.shell_required)

        # Post-installation configuration
        project_full_path = os.path.join(os.getcwd(), safe_name)
        setup_angular_environments(project_full_path)

        typer.secho(
            f"Frontend '{safe_name}' successfully generated and configured!",
            fg=typer.colors.GREEN,
        )
        return True

    except subprocess.CalledProcessError as e:
        typer.secho(f"Error: Angular process failed with code: {e.returncode}", fg=typer.colors.RED)
        return False
