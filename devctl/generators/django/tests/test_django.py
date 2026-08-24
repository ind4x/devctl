import os
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_django_calls_boilerplate():
    """Ensure init django calls the boilerplate generator."""
    with patch("devctl.commands.init.generate_django_boilerplate") as mock_gen:
        mock_gen.return_value = True
        with patch("devctl.commands.init.check_tool"):
            result = runner.invoke(app, ["init", "django", "my-django-app"])
            assert result.exit_code == 0
            mock_gen.assert_called_once_with("my-django-app")


def test_add_resource_django(tmp_path):
    """Ensure add resource works in a Django project."""
    (tmp_path / "manage.py").write_text("import os", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("django", encoding="utf-8")
    (tmp_path / "core").mkdir()

    with patch("devctl.commands.add.generate_django_resource") as mock_gen:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "resource", "User"])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


def test_dockerize_django(tmp_path):
    """Ensure dockerize detects Django and generates a Dockerfile."""
    (tmp_path / "manage.py").write_text("import os", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("django", encoding="utf-8")
    (tmp_path / "core").mkdir()

    result = runner.invoke(app, ["dockerize", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "Dockerfile").exists()
    assert "gunicorn" in (tmp_path / "Dockerfile").read_text()
