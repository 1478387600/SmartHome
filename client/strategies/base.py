# client/strategies/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ..core.mcp_client import MCPClient


class BaseStrategy(ABC):
    """
    每种 LLM 实现一个 Strategy：
    - 根据 `user_query` + 可用工具, 产出 (natural_answer | tool_calls)
    - 如果需要，用 MCPClient.call_tool 继续循环
    """

    def __init__(self, mcp: MCPClient) -> None:
        self.mcp = mcp

    @abstractmethod
    async def chat_loop(self) -> None:
        """运行完整对话循环（读输入 -> 生成回答或工具调用 -> 输出）"""
        ...
