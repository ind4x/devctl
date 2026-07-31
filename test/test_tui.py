import asyncio
from unittest.mock import patch

from typer.testing import CliRunner

from devctl.main import app
from devctl.tui.app import DevctlTUI, make_bar

runner = CliRunner()


def test_make_bar_ranges():
    """Verify that make_bar generates correct Rich styled strings for various percentages."""
    # 0% usage -> all dimmed dots
    bar_0 = make_bar(0, width=10)
    assert "[dim]..........[/dim]" in bar_0
    assert "[dim][[/dim]" in bar_0
    assert "[dim]][/dim]" in bar_0

    # 50% usage -> green blocks
    bar_50 = make_bar(50, width=10)
    assert "[green]|||||[/green]" in bar_50
    assert "[dim].....[/dim]" in bar_50

    # 75% usage -> green and yellow blocks
    bar_75 = make_bar(75, width=12)
    # 50% of 12 is 6 green, 25% of 12 is 3 yellow
    assert "[green]||||||[/green]" in bar_75
    assert "[yellow]|||[/yellow]" in bar_75
    assert "[dim]...[/dim]" in bar_75

    # 100% usage -> green, yellow, and red blocks
    bar_100 = make_bar(100, width=12)
    assert "[green]||||||[/green]" in bar_100
    assert "[yellow]|||[/yellow]" in bar_100
    assert "[red]|||[/red]" in bar_100
    assert "[dim][/dim]" in bar_100 or "[dim]....[/dim]" not in bar_100


def test_tui_command_help():
    """Verify cli runner registers tui commands and options."""
    result = runner.invoke(app, ["tui", "--help"])
    assert result.exit_code == 0
    # Strip ANSI styling codes emitted by Rich/Typer in CI environments
    import re

    clean_output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    assert "--single" in clean_output
    assert "-s" in clean_output


@patch("devctl.tui.app.discover_docker_projects")
@patch("devctl.tui.app.detect_environment")
def test_tui_initialization(mock_detect, mock_discover):
    """Test that DevctlTUI instantiates correctly with projects."""
    mock_discover.return_value = []
    mock_detect.return_value = {"project_root": "/mock/root", "has_spring": False}

    tui = DevctlTUI(single_panel=False)
    assert tui.single_panel is False
    assert tui.selected_service is None
    assert len(tui.projects) == 0

    tui_single = DevctlTUI(single_panel=True)
    assert tui_single.single_panel is True


@patch("devctl.tui.app.discover_docker_projects")
@patch("devctl.tui.app.detect_environment")
def test_tui_compose_flow(mock_detect, mock_discover):
    """Test that compose yields elements without errors in active App context."""
    mock_discover.return_value = []
    mock_detect.return_value = {"project_root": "/mock/root"}

    async def run_tabbed_tui():
        tui = DevctlTUI(single_panel=False)
        async with tui.run_test():
            # Verify widgets are compose mounted
            assert tui.query_one("#tui-tabs") is not None
            assert tui.query_one("#top-nav-helper") is not None

    async def run_single_tui():
        tui = DevctlTUI(single_panel=True)
        async with tui.run_test():
            # Verify widgets are compose mounted
            assert tui.query_one("#single-container") is not None
            assert tui.query_one("#single-system-info") is not None

    asyncio.run(run_tabbed_tui())
    asyncio.run(run_single_tui())
