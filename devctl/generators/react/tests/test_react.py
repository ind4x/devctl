import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_react_calls_boilerplate():
    """Ensure init react calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_react_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "react", "my-react-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-react-app")


def test_add_resource_react(tmp_path):
    """Ensure add resource works in a React project."""
    (tmp_path / "package.json").write_text(
        '{"dependencies": {"react": "18.2.0"}}', encoding="utf-8"
    )
    (tmp_path / "vite.config.ts").write_text("export default {}", encoding="utf-8")

    with patch("devctl.commands.add.generate_react_resource") as mock_gen:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


def test_dockerize_react(tmp_path):
    """Ensure dockerize detects React and generates a Dockerfile."""
    (tmp_path / "package.json").write_text(
        '{"dependencies": {"react": "18.2.0"}}', encoding="utf-8"
    )
    (tmp_path / "vite.config.ts").write_text("export default {}", encoding="utf-8")

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
