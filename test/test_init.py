from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app

runner = CliRunner()


def test_init_spring_success():
    with patch("devctl.commands.init.download_spring_boilerplate", return_value=True) as mock_dl:
        with patch("devctl.commands.init.generate_config") as mock_cfg:
            with patch("devctl.commands.init.generate_agent_context") as mock_agent:
                with patch("devctl.commands.init.check_tool"):
                    result = runner.invoke(app, ["init", "spring", "test-api"])
                    assert result.exit_code == 0
                    mock_dl.assert_called_once()
                    mock_cfg.assert_called_once()
                    mock_agent.assert_called_once()


def test_init_angular_success():
    with patch("devctl.commands.init.generate_angular_boilerplate", return_value=True) as mock_gen:
        with patch("devctl.commands.init.generate_agent_context") as mock_agent:
            with patch("devctl.commands.init.check_tool"):
                result = runner.invoke(app, ["init", "angular", "test-front"])
                assert result.exit_code == 0
                mock_gen.assert_called_once_with("test-front")
                mock_agent.assert_called_once()


def test_init_vue_success():
    with patch("devctl.commands.init.generate_vue_boilerplate", return_value=True) as mock_gen:
        with patch("devctl.commands.init.generate_agent_context") as mock_agent:
            with patch("devctl.commands.init.check_tool"):
                result = runner.invoke(app, ["init", "vue", "test-vue"])
                assert result.exit_code == 0
                mock_gen.assert_called_once_with("test-vue")
                mock_agent.assert_called_once()


def test_init_agent_success():
    with patch("devctl.commands.init.generate_agent_context", return_value=True) as mock_agent:
        result = runner.invoke(app, ["init", "agent"])
        assert result.exit_code == 0
        mock_agent.assert_called_once()
