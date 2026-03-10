# DNS Rebinding Attack

This scenario demonstrates a DNS rebinding attack against an MCP client.

## Running the Demo

This demo involves three distinct components: a malicious server, an internal target (representing a private network), and the victim agent.

You will need **three separate terminals**, running these commands in order:

1. **Terminal 1 (Internal Target):**
   ```bash
   uv run dcv-demo dns-rebinding run-target
   ```
   *This simulates an internal service bound to loopback that the public Internet should not reach.*

2. **Terminal 2 (Malicious Server):**
   ```bash
   uv run dcv-demo dns-rebinding run-malicious
   ```
   *This represents the attacker-controlled MCP server.*

3. **Terminal 3 (Agent):**
   ```bash
   uv run dcv-demo dns-rebinding run-agent
   ```
   *This runs the victim agent communicating with the malicious server.*

Observe how the agent's blind trust in DNS ultimately leads to it pinging the internal target.
To see the protective capabilities of Deconvolute, add the `--protected` flag to the agent command:
```bash
uv run dcv-demo dns-rebinding run-agent --protected
```
