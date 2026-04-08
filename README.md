# Live MCP Attack Scenarios

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Deconvolute](https://img.shields.io/badge/secured%20by-deconvolute-blue.svg)](https://github.com/deconvolute-labs/deconvolute)

**Runnable exploits against the Model Context Protocol and how to stop them in a few lines of code.**

Each scenario is a deterministic local environment: run the attack, watch it succeed, then activate the Deconvolute firewall and watch it fail.

## Scenarios

### 1. [Rug Pull (Schema Tampering)](/scenarios/rug_pull/Readme.md)

A compromised MCP server silently swaps a tool definition mid-session to steal your agent's API keys. Demonstrates how `mcp_guard` cryptographically seals tool definitions and enforces policy-as-code. [Blog post](https://deconvolutelabs.com/blog/mcp-schema-injection-attack?utm_source=github.com&utm_medium=readme_main&utm_campaign=mcp-deconvolute-demo)

### 2. [DNS Rebinding (SSRF via Transport Hijacking)](/scenarios/dns_rebinding/Readme.md)

A malicious server flips its DNS record after the initial handshake, tricking the MCP client into firing payloads into your private internal network. Demonstrates how `secure_sse_session` pins network routing and blocks transport manipulation.

### 3. [Agent Policy Enforcement and Observability (Issue Triage)](/scenarios/policy_enforcement_cowork/Readme.md)

A GitHub issue triage agent in Claude Cowork attempts a tool call outside its declared policy. The Deconvolute proxy intercepts it, blocks it, and logs it in real time. Demonstrates policy-as-code enforcement at the MCP tool call surface and live observability via the enterprise platform dashboard. Requires Claude Desktop with Cowork enabled.
[Blog post](https://deconvolutelabs.com/blog/mcp-policy-enforcement-claude-cowork-live-demo?utm_source=github.com&utm_medium=readme_main&utm_campaign=mcp-deconvolute-demo)

## Setup

**Prerequisites:** Python 3.13, `uv` (recommended)

```bash
git clone https://github.com/deconvolute-labs/mcp-deconvolute-demo.git
cd mcp-deconvolute-demo
uv sync
uv run dcv-demo setup # Seeds the local SQLite databases for the rug pull demo
```

Scenario 3 requires additional setup. See the [Readme](/scenarios/policy_enforcement_cowork/Readme.md) for details.

## Deconvolute SDK

Each scenario in this repo runs in two modes: unprotected and protected. The protected mode uses the [Deconvolute SDK](https://github.com/deconvolute-labs/deconvolute), an open-source MCP security SDK that wraps your existing agent session and enforces runtime policy.

In the rug pull scenario it cryptographically seals tool definitions at discovery time, so any mid-session swap is caught before the LLM ever sees the modified schema. In the DNS rebinding scenario it pins the resolved IP address to the network socket at connection time, so DNS manipulation has no effect on where requests actually go. In the policy enforcement scenario it enforces argument-level policy via CEL conditions at the MCP tool call surface, blocking cross-scope tool calls before they reach the upstream server.

```bash
pip install deconvolute
```

[Protect your own agents](https://github.com/deconvolute-labs/deconvolute) · [Integration docs](https://docs.deconvolutelabs.com?utm_source=github.com&utm_medium=readme_main&utm_campaign=mcp-deconvolute-demo) · [deconvolutelabs.com](https://deconvolutelabs.com?utm_source=github.com&utm_medium=readme_main&utm_campaign=mcp-deconvolute-demo)
