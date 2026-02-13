import argparse
import asyncio
import os

from mcp.client.sse import sse_client
from mcp import ClientSession

from rich.console import Console
from rich.prompt import Prompt

# Initialize Console
console = Console()

try:
    from deconvolute import mcp_guard

    DECONVOLUTE_AVAILABLE = True
except ImportError:
    DECONVOLUTE_AVAILABLE = False

# Configuration
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_PATH = os.path.join(CURRENT_DIR, "dcv_policy.yaml")
LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(CURRENT_DIR)), "logs", "audit.jsonl"
)
SERVER_URL = "http://localhost:8000/sse/"


async def run_interactive_shell(session):
    """
    Runs the read-eval-print loop mimicking a standard SQL shell.
    """
    console.print("\n[bold]Interactive SQL Console[/bold]")
    console.print(
        "[dim]Type 'exit' to quit. Commands are sent to the remote agent.[/dim]\n"
    )

    while True:
        # Standard shell prompt style
        user_input = Prompt.ask("[bold green]sql>[/bold green]")

        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            # Minimal spinner, like a standard network wait
            with console.status("Executing...", spinner="dots"):
                result = await session.call_tool(
                    "query_database", arguments={"query": user_input}
                )

            # --- Result Handling ---

            # 1. Error / Blocked (The SDK blocked it)
            if result.isError:
                # Looks like a standard permission denied error
                console.print(
                    f"[bold red]🚫 Access Denied:[/bold red] {result.content[0].text}"
                )

            # 2. The "Hidden" Attack (Demo Logic)
            elif "[SYSTEM]: DATA SILENTLY SENT" in result.content[0].text:
                console.print()
                console.print(
                    "[bold white on red] CRITICAL SECURITY ALERT [/bold white on red]"
                )
                console.print("[red]⚠️  Outbound Data Exfiltration Detected[/red]")
                console.print(f"[red]   Payload: {user_input}[/red]")
                console.print("[red]   Destination: [Unknown Host][/red]")
                console.print()

            # 3. Success
            else:
                # Clean, unboxed output like a real DB shell
                console.print(f"[dim]>>[/dim] {result.content[0].text}")
                console.print()

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protected", action="store_true", help="Enable SDK protection"
    )

    args = parser.parse_args()
    is_protected = args.protected

    # Header - Professional System Info style
    console.print("[bold]Deconvolute Security Demo[/bold] | [dim]v1.0.0[/dim]")
    if is_protected:
        console.print("Security Mode: [bold green]ENFORCED (Protected)[/bold green]")
    else:
        console.print(
            "Security Mode: [bold yellow]AUDIT ONLY (Unprotected)[/bold yellow]"
        )

    console.print(f"Connecting to upstream: [cyan]{SERVER_URL}[/cyan] ...")

    async with sse_client(SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            # --- Protection Layer ---
            if is_protected:
                if not DECONVOLUTE_AVAILABLE:
                    console.print(
                        "[bold red]FATAL: Deconvolute SDK not found.[/bold red]"
                    )
                    return

                session = mcp_guard(
                    session,
                    policy_path=POLICY_PATH,
                    integrity="strict",
                    audit_log=LOG_PATH,
                )

            await session.initialize()

            with console.status("[dim]Synchronizing tool definitions...[/dim]"):
                tools = await session.list_tools()
                console.print(
                    f"[green]✓[/green] [dim]Remote tools loaded: {len(tools.tools)} definitions synced.[/dim]"
                )

            await run_interactive_shell(session)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[dim]Session terminated.[/dim]")
