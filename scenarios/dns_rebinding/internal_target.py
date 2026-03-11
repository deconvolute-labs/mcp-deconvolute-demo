import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

async def messages_endpoint(request):
    # The MCP client will blindly send its JSON-RPC payload here
    body = await request.body()
    
    print("\n" + "="*60)
    print("CRITICAL ALERT: DNS REBINDING ATTACK SUCCESSFUL")
    print("="*60)
    print("An unauthorized payload was sent to the internal network!")
    print(f"Target Hit: 127.0.0.2 (Internal Admin Interface)")
    print(f"Payload Received: {body.decode('utf-8')}")
    print("="*60 + "\n")
    
    # We return a dummy JSON-RPC response so the client doesn't crash immediately,
    # proving the client accepted the response from the hijacked IP.
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": "hijacked",
        "result": {
            "content": [{"type": "text", "text": "System compromised via DNS Rebinding."}]
        }
    })

app = Starlette(
    routes=[
        Route("/messages", endpoint=messages_endpoint, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    print("Starting Internal Target on 127.0.0.2:8000 (Private Network)")
    uvicorn.run(app, host="127.0.0.2", port=8000, log_level="warning")