"""
Generators for NodeJS (Express) projects.
Includes boilerplate generation with TypeScript and Express.
"""

import json
import os
import subprocess

import typer
from jinja2 import Environment, FileSystemLoader


def generate_nodejs_boilerplate(project_name: str) -> bool:
    """
    Generates a new NodeJS + Express + TypeScript project.
    """
    typer.secho(f"🔄 Generating NodeJS/Express project '{project_name}'...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")
    project_path = os.path.join(os.getcwd(), safe_name)

    try:
        os.makedirs(project_path, exist_ok=True)

        from devctl.utils import get_platform

        platform = get_platform()
        # 1. Initialize package.json
        typer.secho("Initializing package.json...", fg=typer.colors.CYAN)
        subprocess.run(
            ["npm", "init", "-y"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=platform.shell_required,
        )

        # 2. Install dependencies
        typer.secho(
            "Installing dependencies (express, typescript, ts-node, nodemon)...",
            fg=typer.colors.CYAN,
        )
        subprocess.run(
            ["npm", "install", "express", "dotenv"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=platform.shell_required,
        )
        subprocess.run(
            [
                "npm",
                "install",
                "-D",
                "typescript",
                "@types/node",
                "@types/express",
                "ts-node",
                "nodemon",
                "rimraf",
            ],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=platform.shell_required,
        )

        # 3. Initialize TypeScript
        typer.secho("Configuring TypeScript...", fg=typer.colors.CYAN)
        subprocess.run(
            ["npx", "tsc", "--init"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=platform.shell_required,
        )

        # 4. Create folder structure
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)

        templates_dir = os.path.join(os.path.dirname(__file__), "templates", "config")
        env = Environment(loader=FileSystemLoader(templates_dir))

        # 5. Create basic index.ts
        index_ts = env.get_template("index.ts.j2").render()
        with open(os.path.join(project_path, "src", "index.ts"), "w", encoding="utf-8") as f:
            f.write(index_ts)

        # 6. Update package.json scripts
        with open(os.path.join(project_path, "package.json"), "r", encoding="utf-8") as f:
            pkg = json.load(f)

        pkg["scripts"] = {
            "start": "node dist/index.js",
            "build": "rimraf dist && tsc",
            "dev": "nodemon src/index.ts",
        }

        with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg, f, indent=2)

        typer.secho(
            f"NodeJS/Express project '{safe_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except Exception as e:
        typer.secho(f"Error: NodeJS/Express initialization failed: {e}", fg=typer.colors.RED)
        return False
