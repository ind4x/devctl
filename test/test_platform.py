import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from devctl.utils.platform import (
    UnixPlatform,
    WindowsPlatform,
    get_platform,
)


def test_get_platform():
    """Ensure get_platform returns the correct implementation based on sys.platform."""
    with patch("sys.platform", "win32"):
        p = get_platform()
        assert isinstance(p, WindowsPlatform)

    with patch("sys.platform", "linux"):
        p = get_platform()
        assert isinstance(p, UnixPlatform)


def test_windows_platform():
    """Ensure WindowsPlatform returns the correct values and calls taskkill."""
    p = WindowsPlatform()
    assert p.python_exe == "python"
    assert p.mvnw_cmd == "mvnw.cmd"
    assert p.shell_required is True

    path = Path("proj")
    assert p.get_venv_python(path) == os.path.join("proj", ".venv", "Scripts", "python.exe")
    assert p.get_venv_pip(path) == os.path.join("proj", ".venv", "Scripts", "pip.exe")
    assert p.get_venv_django_admin(path) == os.path.join(
        "proj", ".venv", "Scripts", "django-admin.exe"
    )

    # Test kill_process_tree
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    with patch("subprocess.run") as mock_run:
        p.kill_process_tree(mock_proc)
        mock_run.assert_called_once_with(
            ["taskkill", "/F", "/T", "/PID", "1234"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )


def test_unix_platform():
    """Ensure UnixPlatform returns the correct values and terminates/kills process."""
    p = UnixPlatform()
    assert p.python_exe == "python3"
    assert p.mvnw_cmd == "./mvnw"
    assert p.shell_required is False

    path = Path("proj")
    assert p.get_venv_python(path) == os.path.join("proj", ".venv", "bin", "python3")
    assert p.get_venv_pip(path) == os.path.join("proj", ".venv", "bin", "pip")
    assert p.get_venv_django_admin(path) == os.path.join("proj", ".venv", "bin", "django-admin")

    # Test kill_process_tree with normal termination
    mock_proc = MagicMock()
    p.kill_process_tree(mock_proc)
    mock_proc.terminate.assert_called_once()
    mock_proc.wait.assert_called_once_with(timeout=5)
    mock_proc.kill.assert_not_called()
