import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from devctl.generators.docker import DockerProject
from devctl.orchestrator.runner import is_docker_running, launch_dev_environment


def test_is_docker_running_true():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert is_docker_running() is True


def test_is_docker_running_false():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker info")
        assert is_docker_running() is False


def test_launch_dev_environment_empty():
    with patch("typer.secho") as mock_secho:
        launch_dev_environment([], [])
        mock_secho.assert_called_with(
            "Warning: No projects or databases detected to run.", fg="yellow"
        )


@patch("subprocess.Popen")
@patch("subprocess.run")
@patch("time.sleep")
def test_launch_dev_environment_complex(mock_sleep, mock_run, mock_popen):
    # Setup mocks
    mock_popen.return_value = MagicMock(poll=lambda: None)

    projects = [
        DockerProject(
            kind="spring",
            path=Path("/tmp/spring"),
            name="api",
            service_name="api",
            relative_context="./api",
        ),
        DockerProject(
            kind="angular",
            path=Path("/tmp/angular"),
            name="front",
            service_name="front",
            relative_context="./front",
        ),
    ]
    docker_composes = [Path("/tmp/db")]

    # Use an exception that is caught by launch_dev_environment to stop the loop
    mock_sleep.side_effect = Exception("Stop Loop")

    with patch("devctl.orchestrator.runner.is_docker_running", return_value=True):
        with patch("devctl.orchestrator.runner.cleanup_and_exit") as mock_cleanup:
            launch_dev_environment(projects, docker_composes)

            # Verify Docker Compose started
            mock_run.assert_any_call(
                ["docker", "compose", "-f", "docker-compose-db.yml", "up", "-d"],
                cwd="/tmp/db",
                check=True,
            )

            # Verify cleanup called
            mock_cleanup.assert_called_once()


@patch("subprocess.Popen")
@patch("time.sleep")
def test_launch_dev_environment_with_env(mock_sleep, mock_popen, tmp_path):
    # Setup mocks
    mock_popen.return_value = MagicMock(poll=lambda: None)
    mock_sleep.side_effect = Exception("Stop Loop")

    # Create a project with a .env file
    project_path = tmp_path / "spring-app"
    project_path.mkdir()
    (project_path / ".env").write_text("APP_PORT=8081\nSECRET=xyz")

    projects = [
        DockerProject(
            kind="spring",
            path=project_path,
            name="app",
            service_name="app",
            relative_context="./app",
        )
    ]

    with patch("devctl.orchestrator.runner.cleanup_and_exit"):
        try:
            launch_dev_environment(projects, [])
        except Exception:
            pass

        # Verify Popen was called with merged env
        args, kwargs = mock_popen.call_args
        env = kwargs.get("env")
        assert env["APP_PORT"] == "8081"
        assert env["SECRET"] == "xyz"
        assert "PATH" in env  # System env preserved
