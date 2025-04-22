"""
运行模拟客户端，自动加载 example_inputs.json 并依次调用 MCP tool/resource。
"""

import asyncio
import os
import sys
import json
from contextlib import AsyncExitStack

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from client.parser import parse_llm_response
from client.mcp_caller import init_mcp_client, call_tool, read_resource


async def main():
    # 加载 example_inputs.json
    inputs_path = os.path.join("client", "example_inputs.json")
    with open(inputs_path, "r", encoding="utf-8") as f:
        examples = json.load(f)

    print("🤖 Starting MCP Client (batch mode)...")

    async with AsyncExitStack() as stack:
        try:
            session = await init_mcp_client("scripts/run_server.py", stack)
            # session = await init_mcp_client("scripts/test_server.py", stack)
        except Exception as e:
            print(f"❌ MCP client initialization failed: {type(e).__name__}: {e}")
            return

        try:
            for i, example in enumerate(examples):
                print(f"\n▶️  Running Example {i + 1}: {example}")
                try:
                    response = parse_llm_response(json.dumps(example))
                    if response.type == "tool":
                        result = await call_tool(session, response.name, response.arguments)
                    elif response.type == "resource":
                        result = await read_resource(session, response.name)
                    else:
                        result = "[❌ Unknown response type]"
                except Exception as e:
                    result = f"[❌ Error] {str(e)}"

                print(f"✅ Result: {result}")
        except asyncio.CancelledError:
            print("\nShutting down...")
            raise
        except KeyboardInterrupt:
            print("\nShutting down...")
            raise

if __name__ == "__main__":
    asyncio.run(main())
