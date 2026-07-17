"""
Generators for NodeJS (Express) projects.
Includes boilerplate generation with TypeScript and Express.
"""

import json
import os
import subprocess

import typer


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

        # 5. Create basic index.ts
        index_ts = """import express, { Request, Response } from 'express';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req: Request, res: Response) => {
  res.send('Hello from devctl NodeJS/Express!');
});

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});
"""
        with open(os.path.join(project_path, "src", "index.ts"), "w") as f:
            f.write(index_ts)

        # 6. Update package.json scripts
        with open(os.path.join(project_path, "package.json"), "r") as f:
            pkg = json.load(f)

        pkg["scripts"] = {
            "start": "node dist/index.js",
            "build": "rimraf dist && tsc",
            "dev": "nodemon src/index.ts",
        }

        with open(os.path.join(project_path, "package.json"), "w") as f:
            json.dump(pkg, f, indent=2)

        typer.secho(
            f"NodeJS/Express project '{safe_name}' successfully generated!", fg=typer.colors.GREEN
        )
        return True

    except Exception as e:
        typer.secho(f"Error: NodeJS/Express initialization failed: {e}", fg=typer.colors.RED)
        return False
