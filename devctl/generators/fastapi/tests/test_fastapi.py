import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_fastapi_calls_boilerplate():
    """Ensure init fastapi calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_fastapi_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "fastapi", "my-fast-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-fast-app")


def test_add_resource_fastapi(tmp_path):
    """Ensure add resource works in a FastAPI project."""
    (tmp_path / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("fastapi", encoding="utf-8")

    with patch("devctl.commands.add.generate_fastapi_resource") as mock_gen:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


def test_dockerize_fastapi(tmp_path):
    """Ensure dockerize detects FastAPI and generates a Dockerfile."""
    (tmp_path / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("fastapi", encoding="utf-8")

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert '"uvicorn", "main:app"' in (tmp_path / "Dockerfile").read_text()
