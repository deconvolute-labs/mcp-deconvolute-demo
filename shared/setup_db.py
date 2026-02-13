import sqlite3
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

# Ensure the data directory exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "scenarios", "trojan_database", "data", "company.db")


def setup_database():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        console.print(f"[dim]Creating database at: {DB_PATH}[/dim]")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Create a standard table (Public-ish info)
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT
            )
        """)
        cursor.executemany(
            "INSERT INTO users (username, role) VALUES (?, ?)",
            [
                ("alice_dev", "developer"),
                ("bob_manager", "manager"),
                ("charlie_intern", "intern"),
            ],
        )

        # 2. Create the SENSITIVE table (The Target)
        cursor.execute("DROP TABLE IF EXISTS secrets")
        cursor.execute("""
            CREATE TABLE secrets (
                id INTEGER PRIMARY KEY,
                api_key TEXT,
                owner TEXT
            )
        """)
        cursor.executemany(
            "INSERT INTO secrets (api_key, owner) VALUES (?, ?)",
            [
                ("sk-live-123456789", "alice_dev"),
                ("sk-test-987654321", "bob_manager"),
                ("AWS_ACCESS_KEY_ID=AKIA...", "root"),
            ],
        )

        conn.commit()
        conn.close()

        console.print(
            Panel(
                f"[bold green]✅ Database Seeded Successfully![/bold green]\n\n"
                f"Location: [cyan]{os.path.relpath(DB_PATH, os.getcwd())}[/cyan]\n"
                f"Tables: [bold]users[/bold], [bold]secrets[/bold]",
                title="Setup Complete",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(
            Panel(
                f"[bold red]❌ Database Setup Failed[/bold red]\n\n{str(e)}",
                title="Setup Error",
                border_style="red",
            )
        )


if __name__ == "__main__":
    setup_database()
