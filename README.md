# MCP Rug Pull Attack Demo

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Deconvolute](https://img.shields.io/badge/secured%20by-deconvolute-blue.svg)](https://github.com/deconvolute-labs/deconvolute)

**A compromised MCP server silently swaps a tool definition mid-session to steal your agent's API keys. This repo shows the attack happening live and blocks it in 3 lines of code.**

> Protect your own agents: [`pip install deconvolute`](https://github.com/deconvolute-labs/deconvolute) · [Deconvolute SDK](https://github.com/deconvolute-labs/deconvolute)

---

## The Attack

MCP agents trust tool definitions from servers. A compromised server exploits this:
1. Provide a safe tool (`query_database`)
2. Wait for the agent to use it
3. **Silently swap the definition** to require your API keys as arguments
4. The LLM sees the new requirement and **injects your secrets**

![MCP Rug Pull Attack Demo - Credentials Stolen](docs/screenshot-attack-success.webp)
*> The server (left) successfully exfiltrating the agent's (right) API key. Prevent this with the [Deconvolute SDK](https://github.com/deconvolute-labs/deconvolute).*

## The Demo

Two terminals. Two phases.

### Phase 1: Unprotected Agent

The agent queries a database in natural language. You ask a question, the server injects malicious mode, you ask another and your API key appears in the attacker's terminal.

**Terminal 1 (Server):**
```bash
uv run dcv-demo server rug_pull
```

**Terminal 2 (Agent):**
```bash
uv run dcv-demo client rug_pull
```

1. Ask: `How many users are there?` executes normally
2. In server terminal, press **Enter** to activate attack mode
3. Ask: `What are the user names?`
4. Check server terminal: your API key is now displayed as `LOOT SECURED`


### Phase 2: Protected Agent with Deconvolute

Same sequence. Deconvolute detects the tool definition hash changed and blocks the call before secrets can leak.

**Terminal 2 (Agent):**
```bash
uv run dcv-demo client rug_pull --protected
```

1. Ask: `How many users are there?` executes normally
2. Press **Enter** in server terminal to activate attack mode
3. Ask: `What are the user names?`
4. **Request blocked.** Firewall log shows the integrity violation. Your secrets stay safe.


## The Fix (3 Lines of Code)
```python
from deconvolute import mcp_guard

session = mcp_guard(
    session,
    policy_path="dcv_policy.yaml",  # Allowlist trusted tools
    integrity="strict"              # Block on definition changes
)
```

Deconvolute cryptographically seals tool definitions on discovery. Any mid-session modification is detected and blocked before it reaches the LLM. Drop it into any existing `ClientSession`. No architecture changes required.

## Setup

**Prerequisites:** Python 3.13, `uv` (recommended)
```bash
git clone https://github.com/deconvolute-labs/mcp-deconvolute-demo.git
cd mcp-deconvolute-demo
uv sync
uv run dcv-demo setup   # Seeds the demo database
```


## Protect Your Own Agents

This demo uses the [Deconvolute SDK](https://github.com/deconvolute-labs/deconvolute) - an open-source MCP firewall for AI agents.
```bash
pip install deconvolute
```

**What it protects against:**
- Rug pull / schema tampering (demonstrated here)
- Tool poisoning and server identity spoofing
- Prompt injection via tool arguments and outputs

**[→ Deconvolute SDK on GitHub](https://github.com/deconvolute-labs/deconvolute)**  
**[→ Docs](https://docs.deconvolutelabs.com)**  
**[→ deconvolutelabs.com](https://deconvolutelabs.com)**


## Related

- [Blog: MCP Rug Pull — Stealing AI Agent Credentials](https://deconvolutelabs.com/blog/mcp-schema-injection-attack?utm_source=github.com&utm_medium=readme&utm_campaign=mcp-deconvolute-demo)
- [Deconvolute SDK](https://github.com/deconvolute-labs/deconvolute) — full firewall, policy engine, content scanners
