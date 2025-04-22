import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TEST_SERVER_PATH = "scripts/test_server.py"

async def run_test():
    print("🧪 启动 MCP 最小测试")

    server_params = StdioServerParameters(
        command="python",
        args=[TEST_SERVER_PATH]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("📡 正在初始化 handshake ...")
            await session.initialize()
            print("✅ MCP handshake 成功！")

            tools = await session.list_tools()
            print("🔧 可用工具：", [t.name for t in tools])

            result = await session.call_tool("ping", {})
            print("🛠️ 工具调用 ping 返回：", result.content)

if __name__ == "__main__":
    asyncio.run(run_test())
