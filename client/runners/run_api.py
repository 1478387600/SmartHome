"""
client/runners/run_api.py - API Runner for MCP Client

This module implements the main execution flow for running the MCP client
with OpenAI strategy in API mode.

Key Features:
- MCP client session management
- OpenAI strategy integration
- Error handling and logging
- Async execution context

Location: client/runners/run_api.py (relative to project root)

Dependencies:
- asyncio: Async I/O operations
- client.core.mcp_client: MCP client implementation
- client.strategies.openai: OpenAI integration strategy
"""
import asyncio
import os
import subprocess
import sys
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from client.core.mcp_client import MCPClient
from client.strategies.openai import OpenAIStrategy

async def session_with_timeout(mcp_client):
    """
    Create MCP session with timeout handling.
    
    Args:
        mcp_client: MCPClient instance
        
    Returns:
        MCP session or None if connection fails
        
    Note:
        Uses asyncio.to_thread to run synchronous session method asynchronously
    """
    try:
        mcp = await asyncio.to_thread(mcp_client.session)
        return mcp
    except Exception as e:
        print(f"Connection error: {e}")
        return None

async def main() -> None:
    """
    Main execution flow for API runner.
    
    Steps:
    1. Creates MCP client session
    2. Initializes OpenAI strategy
    3. Starts chat loop
    
    Note: Commented code shows alternative server startup approaches
    """
    # Example server startup options (commented out):
    # Option 1: Start server with subprocess
    # subprocess.Popen(["uv", "run", "server/app.py"])
    # subprocess.Popen(
    #     ["uv", "run", "server/app.py"],
    #     stdin=subprocess.DEVNULL,   # Important change
    #     stdout=subprocess.DEVNULL,  # Optional: silence output
    #     stderr=subprocess.DEVNULL,  # Optional: silence errors
    # )

    # Option 2: Alternative session creation
    # try:
    #     print("Initializing MCPClient...")
    #     mcp_client = MCPClient()
    #     print("MCPClient initialized, creating session...")
    #     async with mcp_client.session() as mcp:
    #         print("MCP session created successfully")
    #         strategy = OpenAIStrategy(mcp)
    #         await strategy.chat_loop()
    # except Exception as e:
    #     print(f"Error: {e}")
    #     traceback.print_exc()

    # Primary execution flow
    async with MCPClient().session() as mcp:
        print("MCP session established")
        strategy = OpenAIStrategy(mcp)
        await strategy.chat_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Uncaught error: {e}")
        traceback.print_exc()
