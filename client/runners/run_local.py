# client/runners/run_local.py
import asyncio
import subprocess

from ..core.mcp_client import MCPClient
from ..strategies.local import LocalLLMStrategy


async def main() -> None:
    # 如需自动启动 server
    # subprocess.Popen(["uv", "run", "server/app.py"])
    subprocess.Popen(
        ["uv", "run", "server/app.py"],
        stdin=subprocess.DEVNULL,   # 关键改动
        stdout=subprocess.DEVNULL,  # 可选，让它静默
        stderr=subprocess.DEVNULL,  # 可选，让它静默
    )

    async with MCPClient().session() as mcp:
        await LocalLLMStrategy(mcp).chat_loop()


if __name__ == "__main__":
    asyncio.run(main())
