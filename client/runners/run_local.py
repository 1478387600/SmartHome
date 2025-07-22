"""
client/runners/run_local.py - Local Runner for MCP Client

This module implements the main execution flow for running the MCP client
with local LLM strategy.

Key Features:
- MCP client session management
- Local LLM strategy integration
- Optional server auto-start
- Clean async execution

Location: client/runners/run_local.py (relative to project root)

Dependencies:
- asyncio: Async I/O operations
- client.core.mcp_client: MCP client implementation
- client.strategies.local: Local LLM integration strategy
"""
import asyncio
import subprocess

from ..core.mcp_client import MCPClient
from ..strategies.local import LocalLLMStrategy

async def main() -> None:
    """
    Main execution flow for local runner.
    
    Steps:
    1. (Optional) Starts server process
    2. Creates MCP client session
    3. Initializes local LLM strategy
    4. Starts chat loop
    
    Note: Commented code shows server auto-start options
    """
    # Example server startup options (commented out):
    # subprocess.Popen(["uv", "run", "server/app.py"])
    # subprocess.Popen(
    #     ["uv", "run", "server/app.py"],
    #     stdin=subprocess.DEVNULL,   # Critical change
    #     stdout=subprocess.DEVNULL,  # Optional: silence output
    #     stderr=subprocess.DEVNULL,  # Optional: silence errors
    # )

    async with MCPClient().session() as mcp:
        await LocalLLMStrategy(mcp).chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
