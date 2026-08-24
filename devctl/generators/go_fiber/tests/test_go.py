import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_go_calls_boilerplate():
    """Ensure init go calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_go_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "go", "my-go-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-go-app")


def test_add_resource_go(tmp_path):
    """Ensure add resource works in a Go project."""
    (tmp_path / "go.mod").write_text("module my-go-app", encoding="utf-8")

    with patch("devctl.commands.add.generate_go_resource") as mock_gen:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


def test_dockerize_go(tmp_path):
    """Ensure dockerize detects Go and generates a Dockerfile."""
    (tmp_path / "go.mod").write_text("module my-go-app", encoding="utf-8")

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert "golang" in (tmp_path / "Dockerfile").read_text()
    assert 'CMD ["./main"]' in (tmp_path / "Dockerfile").read_text()
