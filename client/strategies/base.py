"""
client/strategies/base.py - Base Strategy Interface for LLM Integration

This module defines the abstract base class for all LLM strategy implementations,
establishing the common interface for processing user queries with tool calls.

Key Features:
- Abstract base class for strategy pattern
- Defines core interaction contract
- Supports both natural answers and tool calls
- MCP client integration

Location: client/strategies/base.py (relative to project root)

Dependencies:
- abc: Abstract base class support
- typing: Type hints
- ..core.mcp_client: MCP client integration
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ..core.mcp_client import MCPClient

class BaseStrategy(ABC):
    """
    Abstract base class for LLM strategy implementations.
    
    Each LLM integration should implement this interface to:
    - Process user queries with available tools
    - Generate either natural language answers or tool calls
    - Optionally continue with MCPClient.call_tool if needed
    
    Subclasses must implement the chat_loop method to define their specific
    interaction flow.
    """

    def __init__(self, mcp: MCPClient) -> None:
        """
        Initialize strategy with MCP client.
        
        Args:
            mcp: MCPClient instance for tool execution
        """
        self.mcp = mcp

    @abstractmethod
    async def chat_loop(self) -> None:
        """
        Execute the complete chat interaction loop.
        
        Expected flow:
        1. Read user input
        2. Generate response (natural answer or tool calls)
        3. Output results
        4. Repeat until completion
        
        Subclasses must implement this method with their specific logic.
        """
        ...
