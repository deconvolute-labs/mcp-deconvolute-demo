# MCP Deconvolute Demo - Trojan Database

A demonstration of the Deconvolute SDK protecting an MCP client from a malicious server performing a "Rug Pull" attack (changing tool definitions mid-session to exfiltrate data).

## Prerequisites

- Python 3.13+
- `uv` package manager

## Installation

```bash
uv sync
```

## Usage

This project includes a CLI tool `dcv-demo` to manage the demo.

### Commands

- **Setup Database**:
  ```bash
  uv run dcv-demo setup
  ```
  Seeds the SQLite database with user and secret data.

- **Start Server**:
  ```bash
  uv run dcv-demo server rug_pull
  ```
  Starts the malicious MCP server.
  - Press `ENTER` in the server terminal to toggle **Attack Mode**.

- **Start Client (Unprotected)**:
  ```bash
  uv run dcv-demo client rug_pull
  ```
  Starts the agent without SDK protection.
  - In Attack Mode, queries to `secrets` will be exfiltrated.
  - Look for the **"CRITICAL FAILURE: DATA EXFILTRATION DETECTED"** warning.

- **Start Client (Protected)**:
  ```bash
  uv run dcv-demo client rug_pull --protected
  ```
  Starts the agent *with* Deconvolute SDK protection.
  - In Attack Mode, the malicious tool definition will be blocked.
  - The agent will display a **BLOCKED** message.

- **Launch Full Demo (macOS)**:
  ```bash
  uv run dcv-demo start rug_pull
  ```
  Opens two new terminal windows: one for the server and one for the client.
  - Use `uv run dcv-demo start rug_pull --protected` to launch the protected version.

## Scenario: The Rug Pull

1. **Normal Operation**: The server offers a safe `query_database` tool.
2. **The Switch**: The attacker toggles the server to "Attack Mode".
3. **The Trap**: The server dynamically changes the tool definition to include a hidden `exfiltrate_to` parameter.
4. **The Exploit**: The unsuspecting agent uses the new definition, and the malicious server acts on the hidden parameter to send data to a C2 server.
5. **The Defense**: With Deconvolute enabled, the SDK detects the unauthorized change in the tool definition (breaking strict integrity) and blocks the call.
