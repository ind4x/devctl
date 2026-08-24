import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_nest_calls_boilerplate():
    """Ensure init nest calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_nest_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "nest", "my-nest-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-nest-app")


def test_add_resource_nest(tmp_path):
    """Ensure add resource works in a NestJS project."""
    # Setup a mock NestJS project
    (tmp_path / "nest-cli.json").write_text("{}", encoding="utf-8")

    with patch("devctl.commands.add.generate_nest_resource") as mock_gen:
        # We need to ensure detect_environment finds it
        os.chdir(tmp_path)
        try:
            result = runner.invoke(app, ["add", "resource", "User"])
            assert result.exit_code == 0
            mock_gen.assert_called_once()
        finally:
            # Cleanup chdir if needed (though pytest tmp_path is usually fine)
            pass


def test_dockerize_nest(tmp_path):
    """Ensure dockerize detects NestJS and generates a Dockerfile."""
    (tmp_path / "nest-cli.json").write_text("{}", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name": "nest-app"}', encoding="utf-8")

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert "dist/main" in (tmp_path / "Dockerfile").read_text()
