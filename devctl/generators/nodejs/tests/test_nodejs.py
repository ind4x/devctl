import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_nodejs_calls_boilerplate():
    """Ensure init nodejs calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_nodejs_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "nodejs", "my-node-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-node-app")


def test_add_resource_nodejs(tmp_path):
    """Ensure add resource works in a NodeJS project."""
    (tmp_path / "package.json").write_text('{"name": "node-app"}', encoding="utf-8")
    (tmp_path / "src").mkdir()

    with patch("devctl.commands.add.generate_nodejs_resource") as mock_gen:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


def test_dockerize_nodejs(tmp_path):
    """Ensure dockerize detects NodeJS and generates a Dockerfile."""
    (tmp_path / "package.json").write_text('{"name": "node-app"}', encoding="utf-8")

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert 'CMD ["npm", "start"]' in (tmp_path / "Dockerfile").read_text()
