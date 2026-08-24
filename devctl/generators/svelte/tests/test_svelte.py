import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_svelte_calls_boilerplate():
    """Ensure init svelte calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_svelte_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "svelte", "my-svelte-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-svelte-app")


def test_add_resource_svelte(tmp_path):
    """Ensure add resource works in a Svelte project."""
    (tmp_path / "svelte.config.js").write_text("export default {}", encoding="utf-8")

    with patch("devctl.commands.add.generate_svelte_resource") as mock_gen:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


def test_dockerize_svelte(tmp_path):
    """Ensure dockerize detects Svelte and generates a Dockerfile."""
    (tmp_path / "svelte.config.js").write_text("export default {}", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name": "svelte-app"}', encoding="utf-8")

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert 'CMD ["node", "build"]' in (tmp_path / "Dockerfile").read_text()
