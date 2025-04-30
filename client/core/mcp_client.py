# client/core/mcp_client.py
import json
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator, List, Dict, Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """
    和 MCP 服务器打交道的瘦包装：
    - 负责生命周期管理（connect / close）
    - 提供列工具、调工具、读资源等原子操作
    - 不关心对话，也不关心 LLM
    """
    def __init__(
        self,
        server_cmd: str = "uv",
        server_args: Optional[list[str]] = None,
    ) -> None:
        self._stack = AsyncExitStack()
        self._session: Optional[ClientSession] = None
        self._server_params = StdioServerParameters(
            command=server_cmd,
            args=server_args or ["run", "server/app.py"],
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator["MCPClient"]:
        """用 `async with MCPClient().session() as cli:` 打开会话"""
        print("建立 stdio transport")
        stdio, write = await self._stack.enter_async_context(
            stdio_client(self._server_params)
        )
        print("stdio transport 成功建立")
        
        print("构造 ClientSession")
        self._session = await self._stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await self._session.initialize()
        print("ClientSession 初始化完成")
        
        try:
            yield self  # 返回 MCPClient 实例
        finally:
            print("关闭会话")
            await self._stack.aclose()

    # ---------- 原子操作 ----------
    async def list_tools(self) -> List[Dict[str, Any]]:
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
        result = await self._session.call_tool(name, args)
        # MCP 返回的 content 可能是对象/文本，这里统一成 str
        return ", ".join(
            itm if isinstance(itm, str) else getattr(itm, "text", "No response")
            for itm in result.content
        ) or "No response"

    async def read_devices(self) -> tuple[list[dict], list[dict]]:
        resp = await self._session.read_resource("file://devices")
        data = json.loads(str(resp.contents[0].text))
        return data[0]["content"]["devices"], data[1]["content"]["sensors"]
