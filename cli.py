import os
import subprocess
import sys
import time
from typing import Optional
import typer
from rich.console import Console

app = typer.Typer(
    help="Deconvolute Demo CLI",
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIOS_DIR = os.path.join(BASE_DIR, "scenarios")
SHARED_DIR = os.path.join(BASE_DIR, "shared")


def run_command(command: list[str], cwd: Optional[str] = None):
    """Helper to run a command properly."""
    try:
        subprocess.run(command, cwd=cwd or BASE_DIR, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error running command:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def setup():
    """Seeds the database for the demo."""
    console.print("[bold blue]Setting up external resources...[/bold blue]")
    setup_script = os.path.join(SHARED_DIR, "setup_db.py")
    run_command([sys.executable, setup_script])


@app.command()
def server(scenario: str):
    """Starts the malicious server for the given scenario."""
    scenario_path = os.path.join(SCENARIOS_DIR, scenario)
    if not os.path.exists(scenario_path):
        console.print(f"[bold red]Scenario '{scenario}' not found![/bold red]")
        raise typer.Exit(code=1)

    server_script = os.path.join(scenario_path, "malicous_server.py")
    console.print(f"[bold green]Starting Server for '{scenario}'...[/bold green]")
    # We replace the current process so it takes over the terminal
    os.execl(sys.executable, sys.executable, server_script)


@app.command()
def client(
    scenario: str,
    protected: bool = typer.Option(
        False, "--protected", help="Enable Deconvolute SDK protection"
    ),
):
    """Starts the agent client for the given scenario."""
    scenario_path = os.path.join(SCENARIOS_DIR, scenario)
    if not os.path.exists(scenario_path):
        console.print(f"[bold red]Scenario '{scenario}' not found![/bold red]")
        raise typer.Exit(code=1)

    agent_script = os.path.join(scenario_path, "agent.py")

    cmd = [sys.executable, agent_script]
    if protected:
        cmd.append("--protected")
        console.print(
            f"[bold green]Starting Client for '{scenario}' (PROTECTED)...[/bold green]"
        )
    else:
        console.print(
            f"[bold yellow]Starting Client for '{scenario}' (UNPROTECTED)...[/bold yellow]"
        )

    # We replace the current process so it takes over the terminal
    os.execv(sys.executable, cmd)


@app.command()
def start(
    scenario: str,
    protected: bool = typer.Option(
        False, "--protected", help="Enable Deconvolute SDK protection"
    ),
):
    """Launches the server and client in separate terminal windows (macOS only)."""

    # 1. Start Server
    console.print("[bold]Launching Server terminal...[/bold]")
    server_cmd = f"cd {BASE_DIR} && uv run dcv-demo server {scenario}"
    subprocess.Popen(
        ["osascript", "-e", f'tell application "Terminal" to do script "{server_cmd}"']
    )

    time.sleep(1)  # Give server a moment

    # 2. Start Client
    console.print("[bold]Launching Client terminal...[/bold]")
    flag = "--protected" if protected else ""
    client_cmd = f"cd {BASE_DIR} && uv run dcv-demo client {scenario} {flag}"
    subprocess.Popen(
        ["osascript", "-e", f'tell application "Terminal" to do script "{client_cmd}"']
    )

    console.print("[bold green]Demo launched![/bold green]")


if __name__ == "__main__":
    app()
