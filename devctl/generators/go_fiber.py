"""
Generators for Go (Fiber) projects.
Includes boilerplate generation with Fiber framework.
"""

import os
import subprocess

import typer


def generate_go_boilerplate(project_name: str) -> bool:
    """
    Generates a new Go + Fiber project.
    """
    typer.secho(f"Generating Go project '{project_name}'...", fg=typer.colors.CYAN)
    project_path = os.path.join(os.getcwd(), project_name)

    try:
        os.makedirs(project_path, exist_ok=True)

        from devctl.utils import get_platform

        platform = get_platform()
        # 1. Go mod init
        typer.secho("Initializing Go module...", fg=typer.colors.CYAN)
        subprocess.run(
            ["go", "mod", "init", project_name],
            cwd=project_path,
            check=True,
            shell=platform.shell_required,
        )

        # 2. Install Fiber
        typer.secho("Installing Fiber framework...", fg=typer.colors.CYAN)
        subprocess.run(
            ["go", "get", "github.com/gofiber/fiber/v2"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=platform.shell_required,
        )

        # 3. Create main.go
        main_go = """package main

import (
    "log"
    "github.com/gofiber/fiber/v2"
)

func main() {
    app := fiber.New()

    app.Get("/", func(c *fiber.Ctx) error {
        return c.SendString("Hello from devctl Go/Fiber!")
    })

    log.Fatal(app.Listen(":3000"))
}
"""
        with open(os.path.join(project_path, "main.go"), "w") as f:
            f.write(main_go)

        typer.secho(f"Go project '{project_name}' successfully generated!", fg=typer.colors.GREEN)
        return True

    except Exception as e:
        typer.secho(f"Error: Go initialization failed: {e}", fg=typer.colors.RED)
        return False
