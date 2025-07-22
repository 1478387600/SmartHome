"""
client/core/mcp_client.py - MCP (Model Context Protocol) client implementation

This module implements the client-side interface for communicating with MCP servers.
It handles connection lifecycle management and provides atomic operations for
interacting with MCP services.

Key Features:
- Manages server connections and sessions
- Provides tool listing and invocation
- Handles resource reading operations
- Independent of LLM or conversation logic

Location: client/core/mcp_client.py (relative to project root)
"""

import json
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator, List, Dict, Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """
    Thin wrapper for interacting with MCP servers.
    
    Responsibilities:
    - Manages connection lifecycle (connect/close)
    - Provides atomic operations:
      - List available tools
      - Call tools
      - Read resources
    - Does not handle conversation or LLM logic
    """
    def __init__(
        self,
        server_cmd: str = "uv",
        server_args: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize a new MCP client instance.
        
        Args:
            server_cmd (str): Command to start the server (default: "uv")
            server_args (Optional[list[str]]): Arguments for server command
                (default: ["run", "server/app.py"])
        """
        self._stack = AsyncExitStack()
        self._session: Optional[ClientSession] = None
        self._server_params = StdioServerParameters(
            command=server_cmd,
            args=server_args or ["run", "server/app.py"],
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator["MCPClient"]:
        """
        Context manager for MCP client session.
        
        Usage:
            async with MCPClient().session() as cli:
                # use client here
        
        Yields:
            MCPClient: The initialized client instance
            
        Note:
            Automatically handles connection setup and teardown
        """
        print("Establishing stdio transport")
        stdio, write = await self._stack.enter_async_context(
            stdio_client(self._server_params)
        )
        print("stdio transport established successfully")
        
        print("Creating ClientSession")
        self._session = await self._stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await self._session.initialize()
        print("ClientSession initialized")
        
        try:
            yield self  # Return MCPClient instance
        finally:
            print("Closing session")
            await self._stack.aclose()

    # ---------- Atomic Operations ----------
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from the MCP server.
        
        Returns:
            List[Dict[str, Any]]: List of tool dictionaries containing:
                - name: Tool identifier
                - description: Tool purpose/functionality
                - input_schema: Expected input parameters
        """
        resp = await self._session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in resp.tools
        ]

    async def call_tool(self, name: str, args: Dict[str, Any]) -> str:
        """
        Execute a tool on the MCP server.
        
        Args:
            name (str): Name of the tool to call
            args (Dict[str, Any]): Input arguments for the tool
            
        Returns:
            str: Tool response converted to string format
            
        Note:
            Converts various MCP response types to string representation
        """
        result = await self._session.call_tool(name, args)
        # MCP response content may be objects/text - normalize to str
        return ", ".join(
            itm if isinstance(itm, str) else getattr(itm, "text", "No response")
            for itm in result.content
        ) or "No response"

    async def read_devices(self) -> tuple[list[dict], list[dict]]:
        """
        Read device and sensor data from the MCP server.
        
        Returns:
            tuple[list[dict], list[dict]]: Tuple containing:
                - List of device dictionaries
                - List of sensor dictionaries
                
        Note:
            Data is read from the server's 'file://devices' resource
        """
        resp = await self._session.read_resource("file://devices")
        data = json.loads(str(resp.contents[0].text))
        return data[0]["content"]["devices"], data[1]["content"]["sensors"]
