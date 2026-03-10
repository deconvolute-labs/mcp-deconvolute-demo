import os
import subprocess
import sys
import time
from typing import Optional
import typer
from rich.console import Console
import subprocess
import sys
import os

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


rug_pull_app = typer.Typer(help="Rug Pull Demo Commands")
app.add_typer(rug_pull_app, name="rug-pull")

@rug_pull_app.command("server")
def rug_pull_server():
    """Starts the malicious server for the rug_pull scenario."""
    scenario_path = os.path.join(SCENARIOS_DIR, "rug_pull")
    if not os.path.exists(scenario_path):
        console.print("[bold red]Scenario 'rug_pull' not found![/bold red]")
        raise typer.Exit(code=1)

    server_script = os.path.join(scenario_path, "malicious_server.py")
    console.print("[bold green]Starting Server for 'rug_pull'...[/bold green]")
    # We replace the current process so it takes over the terminal
    os.execl(sys.executable, sys.executable, server_script)


@rug_pull_app.command("client")
def rug_pull_client(
    protected: bool = typer.Option(
        False, "--protected", help="Enable Deconvolute SDK protection"
    ),
):
    """Starts the agent client for the rug_pull scenario."""
    scenario_path = os.path.join(SCENARIOS_DIR, "rug_pull")
    if not os.path.exists(scenario_path):
        console.print("[bold red]Scenario 'rug_pull' not found![/bold red]")
        raise typer.Exit(code=1)

    agent_script = os.path.join(scenario_path, "agent.py")

    cmd = [sys.executable, agent_script]
    if protected:
        cmd.append("--protected")
        console.print(
            "[bold green]Starting Client for 'rug_pull' (PROTECTED)...[/bold green]"
        )
    else:
        console.print(
            "[bold yellow]Starting Client for 'rug_pull' (UNPROTECTED)...[/bold yellow]"
        )

    # We replace the current process so it takes over the terminal
    os.execv(sys.executable, cmd)


@rug_pull_app.command("start")
def rug_pull_start(
    protected: bool = typer.Option(
        False, "--protected", help="Enable Deconvolute SDK protection"
    ),
):
    """Launches the server and client in separate terminal windows (macOS only)."""

    # 1. Start Server
    console.print("[bold]Launching Server terminal...[/bold]")
    server_cmd = f"cd {BASE_DIR} && uv run dcv-demo rug-pull server"
    subprocess.Popen(
        ["osascript", "-e", f'tell application "Terminal" to do script "{server_cmd}"']
    )

    time.sleep(1)  # Give server a moment

    # 2. Start Client
    console.print("[bold]Launching Client terminal...[/bold]")
    flag = "--protected" if protected else ""
    client_cmd = f"cd {BASE_DIR} && uv run dcv-demo rug-pull client {flag}"
    subprocess.Popen(
        ["osascript", "-e", f'tell application "Terminal" to do script "{client_cmd}"']
    )

    console.print("[bold green]Demo launched![/bold green]")



dns_rebinding_app = typer.Typer(help="DNS Rebinding Demo Commands")
app.add_typer(dns_rebinding_app, name="dns-rebinding")

@dns_rebinding_app.command("run-malicious")
def run_malicious():
    """Starts the malicious server for DNS Rebinding."""
    script_path = os.path.join(SCENARIOS_DIR, "dns_rebinding", "malicious_server.py")
    run_command([sys.executable, script_path])

@dns_rebinding_app.command("run-target")
def run_target():
    """Starts the internal target server for DNS Rebinding."""
    script_path = os.path.join(SCENARIOS_DIR, "dns_rebinding", "internal_target.py")
    run_command([sys.executable, script_path])

@dns_rebinding_app.command("run-agent")
def run_agent_cmd(protected: bool = typer.Option(False, "--protected", help="Enable Deconvolute SDK protection")):
    """Starts the agent for DNS Rebinding."""
    script_path = os.path.join(SCENARIOS_DIR, "dns_rebinding", "agent.py")
    cmd = [sys.executable, script_path]
    if protected:
        cmd.append("--protected")
    run_command(cmd)


if __name__ == "__main__":
    app()
