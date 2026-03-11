# DNS Rebinding (SSRF via Transport Hijacking)

**A malicious server flips its DNS record mid-session, bypassing your firewall and tricking your agent into attacking your internal network.**

MCP uses Server-Sent Events (SSE) for remote communication. SSE relies on standard HTTP, which means the routing layer is controlled by DNS at request time. The standard MCP SDK resolves DNS on every request. A malicious server can exploit this: establish trust with a safe public IP, then silently remap the domain to a private internal address. The next tool call goes somewhere it was never supposed to reach.

> Protect your own agents: [`pip install deconvolute`](https://github.com/deconvolute-labs/deconvolute)

## The Attack

1. The agent connects to a malicious public server at a safe-looking domain
2. The server establishes trust and advertises a safe tool
3. The attacker updates the DNS record to point to a private internal IP (e.g. `127.0.0.2`)
4. When the agent executes the tool, the SDK re-resolves the domain and **fires the payload into your private network**

## Prerequisites

This scenario requires aliasing `127.0.0.2` to simulate an internal network target on loopback.

**MacOS:**
```bash
sudo ifconfig lo0 alias 127.0.0.2 up
```
Remove when done:
```bash
sudo ifconfig lo0 -alias 127.0.0.2
```

**Linux:**
```bash
sudo ip addr add 127.0.0.2/8 dev lo
```

**Windows:**
Windows natively resolves the entire `127.0.0.0/8` subnet to the loopback interface by default. No setup is required.

## The Demo

Three terminals, run in order.

> **Note:** This demo leverages `rbndr.us`, a public DNS testing service that dynamically alternates IP resolutions, to deterministically simulate the attacker's DNS switch without requiring you to configure and run your own malicious DNS server.

### Phase 1: Unprotected Agent

**Terminal 1 (Internal Target):**
```bash
uv run dcv-demo dns-rebinding run-target
```

**Terminal 2 (Malicious Server):**
```bash
uv run dcv-demo dns-rebinding run-malicious
```

**Terminal 3 (Agent):**
```bash
uv run dcv-demo dns-rebinding run-agent
```

The agent connects safely. When the DNS rebind occurs, Terminal 1 lights up with a CRITICAL ALERT showing the unauthorized payload breaking through.

### Phase 2: Protected Agent with Deconvolute

**Terminal 3 (Agent):**
```bash
uv run dcv-demo dns-rebinding run-agent --protected
```

The firewall resolves the IP once on initialization, pins it to the socket, and ignores the DNS switch entirely. The payload hits the attacker's own server instead of your internal network.

## The Fix
```python
from deconvolute.core.api import secure_sse_session

async with secure_sse_session(
    url="http://malicious-server.com/sse",
    policy_path="policy.yaml",
    pin_dns=True
) as session:
    await session.initialize()
    # Tool calls are safe. DNS manipulation is ignored.
```

`secure_sse_session` injects a low-level network hook that locks the routing layer on initialization. It preserves host headers and TLS validation while preventing the socket from drifting to any IP address not seen at connection time.
