"""
MCP 调用执行模块。

该模块通过 MCP Client API 将解析后的调用请求发送到 server，获取响应结果，并返回给主程序。
"""
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def init_mcp_client(server_script_path: str, stack: AsyncExitStack) -> ClientSession:
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path]
    )

    stdio_transport = None
    session = None
    try:
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        session = await stack.enter_async_context(ClientSession(*stdio_transport))
        print("📡 MCP server subprocess launched. Waiting for handshake...")

        # 设置超时时间，避免长时间挂起
        await asyncio.wait_for(session.initialize(), timeout=15)  # 增加超时时间到15秒

        print("✅ MCP client session initialized.")
        tools = await session.list_tools()
        print("🔧 Server registered tools:", [t.name for t in tools.tools])
        return session

    except asyncio.TimeoutError:
        print("[⏱️ Timeout] MCP server did not respond to handshake within 5 seconds.")
        raise

    except Exception as e:
        print(f"[❌ MCP handshake failed: {type(e).__name__}] {e}")
        if session:
            try:
                await session.close()
            except:
                pass
        if stdio_transport:
            try:
                await stdio_transport.close()
            except:
                pass
        raise

async def call_tool(session: ClientSession, tool_name: str, args: dict) -> str:
    """
    调用 MCP Server 上注册的工具函数。

    参数:
        session: 当前 MCP 客户端会话
        tool_name: 工具函数名
        args: 调用参数

    返回:
        工具执行返回值
    """
    print(f"🛠️ Calling tool '{tool_name}' with args {args}")
    try:
        result = await session.call_tool(tool_name, args)
        return str(result)
    except Exception as e:
        return f"Error calling tool {tool_name}: {str(e)}"

async def read_resource(session: ClientSession, resource_uri: str) -> str:
    """
    从 MCP Server 读取资源内容。

    参数:
        session: 当前 MCP 客户端会话
        resource_uri: 资源路径（如 sensor://indoor-temperature）

    返回:
        资源内容字符串
    """
    print(f"📥 Reading resource '{resource_uri}'")
    try:
        result = await session.read_resource(resource_uri)
        return str(result)
    except Exception as e:
        return f"Error reading resource {resource_uri}: {str(e)}"
