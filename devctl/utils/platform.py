"""
Platform abstraction layer to handle OS-specific command execution, paths, and process management.
"""

import os
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path


class BasePlatform(ABC):
    @property
    @abstractmethod
    def python_exe(self) -> str:
        """Global python executable name."""
        pass

    @property
    @abstractmethod
    def mvnw_cmd(self) -> str:
        """Maven wrapper command/script name."""
        pass

    @property
    @abstractmethod
    def shell_required(self) -> bool:
        """Indicates if shell execution is required for subprocess commands."""
        pass

    @abstractmethod
    def get_venv_python(self, project_path: Path) -> str:
        """Returns the path to the python executable in the virtual environment."""
        pass

    @abstractmethod
    def get_venv_pip(self, project_path: Path) -> str:
        """Returns the path to the pip executable in the virtual environment."""
        pass

    @abstractmethod
    def get_venv_django_admin(self, project_path: Path) -> str:
        """Returns the path to the django-admin executable in the virtual environment."""
        pass

    @abstractmethod
    def kill_process_tree(self, proc: subprocess.Popen) -> None:
        """Terminates the process and all its descendants."""
        pass


class WindowsPlatform(BasePlatform):
    @property
    def python_exe(self) -> str:
        return "python"

    @property
    def mvnw_cmd(self) -> str:
        return "mvnw.cmd"

    @property
    def shell_required(self) -> bool:
        return True

    def get_venv_python(self, project_path: Path) -> str:
        return os.path.join(str(project_path), ".venv", "Scripts", "python.exe")

    def get_venv_pip(self, project_path: Path) -> str:
        return os.path.join(str(project_path), ".venv", "Scripts", "pip.exe")

    def get_venv_django_admin(self, project_path: Path) -> str:
        return os.path.join(str(project_path), ".venv", "Scripts", "django-admin.exe")

    def kill_process_tree(self, proc: subprocess.Popen) -> None:
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass


class UnixPlatform(BasePlatform):
    @property
    def python_exe(self) -> str:
        return "python3"

    @property
    def mvnw_cmd(self) -> str:
        return "./mvnw"

    @property
    def shell_required(self) -> bool:
        return False

    def get_venv_python(self, project_path: Path) -> str:
        return os.path.join(str(project_path), ".venv", "bin", "python3")

    def get_venv_pip(self, project_path: Path) -> str:
        return os.path.join(str(project_path), ".venv", "bin", "pip")

    def get_venv_django_admin(self, project_path: Path) -> str:
        return os.path.join(str(project_path), ".venv", "bin", "django-admin")

    def kill_process_tree(self, proc: subprocess.Popen) -> None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def get_platform() -> BasePlatform:
    """Factory function to return the correct Platform implementation."""
    if sys.platform == "win32":
        return WindowsPlatform()
    return UnixPlatform()
