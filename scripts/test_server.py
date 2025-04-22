# scripts/test_server.py

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TestServer")

@mcp.tool()
def ping() -> str:
    return "pong"

if __name__ == "__main__":
    print("TestServer starting...")
    mcp.run(transport="stdio")
