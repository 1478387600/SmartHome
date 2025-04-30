# client/runners/run_api.py
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
    try:
        # 使用 asyncio.to_thread 将同步方法转为异步执行
        mcp = await asyncio.to_thread(mcp_client.session)
        return mcp
    except Exception as e:
        print(f"连接错误: {e}")
        return None

async def main() -> None:
    # ① 如需自动拉起 server，可用 subprocess；否则删掉
    # subprocess.Popen(["uv", "run", "server/app.py"])
    # subprocess.Popen(
    #     ["uv", "run", "server/app.py"],
    #     stdin=subprocess.DEVNULL,   # 关键改动
    #     stdout=subprocess.DEVNULL,  # 可选，让它静默
    #     stderr=subprocess.DEVNULL,  # 可选，让它静默
    # )

    # try:
    #     print("正在初始化 MCPClient...")
    #     mcp_client = MCPClient()
    #     print("MCPClient 初始化完成，正在创建会话...")

    #     # 使用 async with 获取会话对象
    #     async with mcp_client.session() as mcp:
    #         print("MCP 会话创建成功")
    #         strategy = OpenAIStrategy(mcp)
    #         await strategy.chat_loop()

    # except Exception as e:
    #     print(f"Error: {e}")
    #     traceback.print_exc()

    # ② 建立 MCP 会话
    # try:
    #     # 使用 asyncio.to_thread 将同步方法转为异步执行
    #     mcp = await asyncio.to_thread(MCPClient().session)
    #     return mcp
    # except Exception as e:
    #     print(f"连接错误: {e}")
    # print(f"entered")
    async with MCPClient().session() as mcp:
        print(f"with MCPClient().session() entered")
        strategy = OpenAIStrategy(mcp)
        await strategy.chat_loop()


if __name__ == "__main__":
    # asyncio.run(main())

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Uncaught error: {e}")
        traceback.print_exc()
