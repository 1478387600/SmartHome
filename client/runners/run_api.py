# client/runners/run_api.py
import asyncio
import subprocess

from ..core.mcp_client import MCPClient
from ..strategies.openai import OpenAIStrategy


async def main() -> None:
    # ① 如需自动拉起 server，可用 subprocess；否则删掉
    # subprocess.Popen(["uv", "run", "server/app.py"])
    # subprocess.Popen(
    #     ["uv", "run", "server/app.py"],
    #     stdin=subprocess.DEVNULL,   # 关键改动
    #     stdout=subprocess.DEVNULL,  # 可选，让它静默
    #     stderr=subprocess.DEVNULL,  # 可选，让它静默
    # )

    # ② 建立 MCP 会话
    async with MCPClient().session() as mcp:
        strategy = OpenAIStrategy(mcp)
        await strategy.chat_loop()


if __name__ == "__main__":
    asyncio.run(main())
