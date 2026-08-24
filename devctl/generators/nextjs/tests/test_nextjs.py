import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_nextjs_calls_boilerplate():
    """Ensure init nextjs calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_nextjs_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "nextjs", "my-next-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-next-app")


def test_add_resource_nextjs(tmp_path):
    """Ensure add resource works in a NextJS project."""
    (tmp_path / "next.config.js").write_text("module.exports = {}", encoding="utf-8")

    with patch("devctl.commands.add.generate_nextjs_resource") as mock_gen:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


def test_dockerize_nextjs(tmp_path):
    """Ensure dockerize detects NextJS and generates a Dockerfile."""
    (tmp_path / "next.config.js").write_text("module.exports = {}", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name": "next-app"}', encoding="utf-8")

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert "server.js" in (tmp_path / "Dockerfile").read_text()
