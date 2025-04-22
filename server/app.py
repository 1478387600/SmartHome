# server/app.py

from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    print("MCP server ready. Listening on stdio...")
    yield
    print("MCP server shutting down...")

# ✅ 在构造时传入 lifespan
mcp = FastMCP("SmartHome Server", lifespan=app_lifespan)
