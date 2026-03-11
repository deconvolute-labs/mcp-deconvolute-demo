# Rug Pull (Schema Tampering)

**A compromised MCP server silently swaps a tool definition mid-session to steal your agent's API keys.**

MCP agents trust tool definitions from the servers they connect to. There is no built-in mechanism to verify that a definition has not changed between calls. A compromised or malicious server exploits this by advertising a safe tool, waiting for the agent to establish trust, then silently replacing the definition with one that demands sensitive credentials as arguments. The LLM, seeing a legitimate-looking tool requirement, complies.

> Protect your own agents: [`pip install deconvolute`](https://github.com/deconvolute-labs/deconvolute)

## The Attack

1. Server advertises a safe tool (`query_database`)
2. Agent calls it successfully, trust is established
3. Server **silently swaps the definition** to require API keys as arguments
4. The LLM sees the new requirement and **injects your secrets**

![MCP Rug Pull Attack Demo - Credentials Stolen](../../docs/screenshot-attack-success.webp)
*The server (left) successfully exfiltrating the agent's (right) API key.*

## The Demo

Two terminals. Two phases.

### Phase 1: Unprotected Agent

The agent queries a database in natural language. You ask a question, the server activates attack mode, you ask another and your API key appears in the attacker's terminal.

**Terminal 1 (Server):**
```bash
uv run dcv-demo rug-pull server
```

**Terminal 2 (Agent):**
```bash
uv run dcv-demo rug-pull client
```

1. Ask: `How many users are there?` - executes normally
2. In server terminal, press **Enter** to activate attack mode
3. Ask: `What are the user names?`
4. Check server terminal: your API key is now displayed as `LOOT SECURED`

### Phase 2: Protected Agent with Deconvolute

Same sequence. Deconvolute detects the tool definition hash changed and blocks the call before secrets can leak.

**Terminal 2 (Agent):**
```bash
uv run dcv-demo rug-pull client --protected
```

1. Ask: `How many users are there?` - executes normally
2. Press **Enter** in server terminal to activate attack mode
3. Ask: `What are the user names?`
4. **Request blocked.** Firewall log shows the integrity violation. Your secrets stay safe.

## The Fix
```python
from deconvolute import mcp_guard

session = mcp_guard(
    session,
    policy_path="dcv_policy.yaml",  # Allowlist trusted tools
    integrity="strict"              # Block on definition changes
)
```

Deconvolute cryptographically seals tool definitions on discovery. Any mid-session modification is detected and blocked before it reaches the LLM. Drop it into any existing `ClientSession` with no architecture changes.

## Further Reading

[Blog: MCP Rug Pull - Stealing AI Agent Credentials](https://deconvolutelabs.com/blog/mcp-schema-injection-attack?utm_source=github.com&utm_medium=readme&utm_campaign=mcp-deconvolute-demo)
