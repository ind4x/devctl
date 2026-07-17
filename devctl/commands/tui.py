"""
CLI command group for launching the interactive TUI.
"""

import typer

app = typer.Typer(help="Interactive Terminal User Interface.")


@app.callback(invoke_without_command=True)
def launch_tui(
    ctx: typer.Context,
    single: bool = typer.Option(
        False, "--single", "-s", help="Launch the single-panel dashboard layout."
    ),
):
    """
    Launches the interactive btop-like management interface.
    """
    if ctx.invoked_subcommand is not None:
        return

    typer.secho("Initializing interactive Devctl TUI...", fg=typer.colors.CYAN)

    try:
        from devctl.tui.app import DevctlTUI

        tui_app = DevctlTUI(single_panel=single)
        tui_app.run()
    except Exception as e:
        typer.secho(f"Error launching TUI: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from e
