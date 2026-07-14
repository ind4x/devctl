"""
Generators for FastAPI projects.
Includes boilerplate generation with Uvicorn and Pydantic.
"""

import os
import subprocess

import typer


def generate_fastapi_boilerplate(project_name: str) -> bool:
    """
    Generates a new FastAPI project.
    """
    typer.secho(f"Generating FastAPI project '{project_name}'...", fg=typer.colors.CYAN)
    safe_name = project_name.lower().replace("_", "-")
    project_path = os.path.join(os.getcwd(), safe_name)

    try:
        os.makedirs(project_path, exist_ok=True)

        # 1. Create main.py
        main_py = """from fastapi import FastAPI

app = FastAPI(title="devctl FastAPI project")

@app.get("/")
def read_root():
    return {"Hello": "from devctl FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
"""
        with open(os.path.join(project_path, "main.py"), "w") as f:
            f.write(main_py)

        # 2. Create requirements.txt
        requirements = """fastapi
uvicorn[standard]
pydantic
"""
        with open(os.path.join(project_path, "requirements.txt"), "w") as f:
            f.write(requirements)

        import sys
        python_exe = "python" if sys.platform == "win32" else "python3"

        # 3. Create virtual environment
        typer.secho("Creating virtual environment...", fg=typer.colors.CYAN)
        subprocess.run(
            [python_exe, "-m", "venv", ".venv"],
            cwd=project_path,
            check=True,
            shell=(sys.platform == "win32"),
        )

        # 4. Install dependencies
        typer.secho("Installing dependencies (fastapi, uvicorn)...", fg=typer.colors.CYAN)
        if sys.platform == "win32":
            pip_path = os.path.join(".venv", "Scripts", "pip.exe")
        else:
            pip_path = os.path.join(".venv", "bin", "pip")
        subprocess.run(
            [pip_path, "install", "-r", "requirements.txt"],
            cwd=project_path,
            check=True,
            stdout=subprocess.DEVNULL,
            shell=(sys.platform == "win32"),
        )

        typer.secho(f"FastAPI project '{safe_name}' successfully generated!", fg=typer.colors.GREEN)
        return True

    except Exception as e:
        typer.secho(f"Error: FastAPI initialization failed: {e}", fg=typer.colors.RED)
        return False
