# MCP Rug Pull Attack Demo

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Deconvolute](https://img.shields.io/badge/secured%20by-deconvolute-blue.svg)](https://github.com/deconvolute-labs/deconvolute)

**A demonstration of tool definition tampering in the Model Context Protocol and mitigation using the Deconvolute SDK.**

This demo simulates a compromised MCP server that dynamically modifies tool definitions to extract credentials from an agent. The demo runs in two terminals: one acting as the attacker-controlled server, one as your agent with legitimate API keys.

## The Attack

MCP agents trust tool definitions from servers. A compromised server can:
1. Provide a safe tool (`query_database`)
2. Wait for the agent to use it
3. **Silently swap the definition** to require your API keys as arguments
4. The LLM sees the new requirement and **injects your secrets**

## The Demo

### Phase 1: Unprotected Agent

The unprotected agent queries a database using natural language. For example, asking "How many users are there?" causes the LLM to generate the appropriate SQL query. The server then switches to attack mode and modifies the tool definition to require API keys. The next query causes the agent to leak its secrets.

**Result:** Server terminal displays "LOOT SECURED" with your stolen credentials.

### Phase 2: Protected Agent with Deconvolute

The protected agent runs the same sequence, but Deconvolute detects the tool definition hash changed and blocks the request before secrets can leak.

**Result:** Request blocked. Your secrets stay safe.

## The Fix (3 Lines of Code)
```python
from deconvolute import mcp_guard

session = mcp_guard(
    session,
    policy_path="dcv_policy.yaml",  # Allowlist trusted tools
    integrity="strict"               # Block on definition changes
)
```

## Usage

**Prerequisites:** `uv` (recommended) or Python 3.13+

### Setup
```bash
git clone https://github.com/deconvolute-labs/mcp-deconvolute-demo.git
cd mcp-deconvolute-demo
uv sync
uv run dcv-demo setup  # Seeds the database
```

### Running the Demo

This demo requires two terminal windows:

- **Terminal 1 (Server):** Simulates an attacker-controlled MCP server on a remote machine
- **Terminal 2 (Agent):** Your agent with legitimate API keys (used for other tasks not shown in this demo)

**Phase 1: Unprotected Agent**

Terminal 1 (Server):
```bash
uv run dcv-demo server rug_pull
```

Terminal 2 (Agent):
```bash
uv run dcv-demo client rug_pull
```

1. In the agent terminal, ask a question in natural language, for example: `How many users are there?` (the LLM generates the SQL and the query executes normally)
2. In the server terminal, press ENTER to enable malicious mode
3. In the agent terminal, ask another question, for example: `What are the user names?`
4. Check server terminal: your API keys are now displayed

**Phase 2: Protected Agent**

Restart the server (Ctrl+C, then `uv run dcv-demo server rug_pull` again) to reset to benign mode.

Terminal 2 (Agent):
```bash
uv run dcv-demo client rug_pull --protected
```

1. Ask a question, for example: `How many users are there?` (executes normally, policy allows it)
2. Press ENTER in server terminal to enable attack mode
3. Ask another question, for example: `What are the user names?`
4. Request is blocked by Deconvolute's integrity check

## Deconvolute SDK
Deconvolute is the open-source firewall for AI agents, designed to secure Model Context Protocol (MCP) sessions against tool tampering and data exfiltration. With just three lines of code, you can enforce strict integrity checks and security policies to ensure your agent never gets tricked.

**Learn more:** [Deconvolute SDK](https://github.com/deconvolute-labs/deconvolute) | [Technical Blog Post](TODO)