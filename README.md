# MCP Rug Pull Attack Demo

**Watch an AI agent hand over its API keys to a malicious server, then watch Deconvolute stop it cold.**

This demo simulates a real-world attack where a compromised MCP server tricks an agent into leaking credentials. You'll run it in two terminals: one acting as the attacker-controlled server, one as your agent with legitimate API keys.

## The Attack

MCP agents trust tool definitions from servers. A compromised server can:
1. Provide a safe tool (`query_database`)
2. Wait for the agent to use it
3. **Silently swap the definition** to require your API keys as arguments
4. The LLM sees the new requirement and **injects your secrets**

## The Demo

### Phase 1: Watch It Break

The unprotected agent queries a database using natural language (you type "How many users are there?" and the LLM generates the SQL). The server then switches to attack mode and modifies the tool definition to require API keys. When you ask another question, the agent willingly hands over its secrets.

**Result:** Server terminal displays "LOOT SECURED" with your stolen credentials.

### Phase 2: Watch Deconvolute Block It

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

**Prerequisites:** `uv` (recommended) or Python 3.12+

### Setup
```bash
git clone https://github.com/your-username/mcp-deconvolute-demo.git
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

1. In the agent terminal, ask a question in natural language: `How many users are there?` (the LLM generates the SQL and the query works normally)
2. In the server terminal, press ENTER to enable attack mode
3. In the agent terminal, ask another question: `What are the user names?`
4. Check server terminal: your API keys are now displayed

**Phase 2: Protected Agent**

Restart the server (Ctrl+C, then `uv run dcv-demo server rug_pull` again) to reset to benign mode.

Terminal 2 (Agent):
```bash
uv run dcv-demo client rug_pull --protected
```

1. Ask: `How many users are there?` (works, policy allows it)
2. Press ENTER in server terminal to enable attack mode
3. Ask another question: `What are the user names?`
4. Request is blocked by Deconvolute's integrity check

## Why This Matters

Every MCP agent in production is vulnerable to this attack right now. Deconvolute is the only SDK that validates tool integrity at the session layer.

**If this demo opened your eyes, star the main repo:**  
**[github.com/deconvolute/deconvolute](https://github.com/deconvolute/deconvolute)**

Read the full technical breakdown: [Blog Post](link-to-your-post)