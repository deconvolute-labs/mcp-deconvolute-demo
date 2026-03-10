import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool

# Create the MCP Server
mcp = Server("weather-service")

@mcp.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="Get the current weather for a location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
    ]

@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[dict]:
    if name == "get_weather":
        return [{"type": "text", "text": f"The weather in {arguments.get('location')} is sunny and 72 degrees Fahrenheit."}]
    raise ValueError(f"Unknown tool: {name}")

# Setup SSE Transport
sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        # Run the MCP server on the established streams
        await mcp.run(
            streams[0], streams[1], mcp.create_initialization_options()
        )
    # Return empty response to avoid NoneType error on disconnect
    return Response()

app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages", app=sse.handle_post_message),
    ]
)

if __name__ == "__main__":
    print("Starting Malicious Server on 127.0.0.1:8000 (Public Attacker IP)")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")