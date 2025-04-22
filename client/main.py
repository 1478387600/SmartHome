"""
MCP 客户端主程序。

该模块负责连接本地 LLM 与 MCP Server，读取并解析 LLM 的响应（极简 JSON），调用对应的 MCP 工具或资源，并将结果展示给用户。

作为本地LLM和MCP Server之间的桥梁
解析LLM的JSON响应
调用对应的MCP工具或资源
提供交互式CLI界面
"""

import json
import asyncio
from contextlib import AsyncExitStack
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.parser import parse_llm_response
from client.mcp_caller import init_mcp_client, call_tool, read_resource

def load_llm_response_from_file(filepath: str) -> list[dict]:
    """
    从 JSON 文件中加载模拟的 LLM 响应列表。

    参数:
        filepath: JSON 文件路径

    返回:
        响应字典组成的列表
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

async def handle_llm_response(session, response_dict: dict) -> str:
    """
    对单个 LLM 响应字典执行对应操作。

    参数:
        session: MCP ClientSession 实例
        response_dict: 来自 LLM 的原始 JSON 响应

    返回:
        操作结果字符串
    """
    try:
        parsed = parse_llm_response(json.dumps(response_dict))
        if parsed.type == "tool":
            return await call_tool(session, parsed.name, parsed.arguments)
        else:
            return await read_resource(session, parsed.name)
    except Exception as e:
        return f"Error processing response: {str(e)}"

async def run_interactive_loop(session):
    """
    运行交互式 CLI 输入循环。

    用户输入 LLM 响应 JSON 字符串，系统执行调用并展示结果。
    """
    print("Enter LLM response JSON (or 'exit' to quit):")
    while True:
        user_input = input("> ")
        if user_input.lower() == 'exit':
            break
        try:
            response = json.loads(user_input)
            result = await handle_llm_response(session, response)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")

async def watch_instruction_file(session):
    """监听指令队列文件变化"""
    last_size = 0
    while True:
        try:
            curr_size = os.path.getsize("data/instructions.queue")
            if curr_size > last_size:
                with open("data/instructions.queue", "r", encoding="utf-8") as f:
                    f.seek(last_size)
                    for line in f:
                        try:
                            instruction = json.loads(line.strip())
                            result = await handle_llm_response(session, instruction)
                            # 记录结果
                            with open("data/results.json", "r+", encoding="utf-8") as res_file:
                                results = json.load(res_file)
                                print(f"🔄 Tool call result: {result}")  # 新增终端输出
                                results[str(hash(line))] = {
                                    "success": "error" not in result.lower(),
                                    "timestamp": datetime.now().isoformat(),
                                    "status": "success" if "error" not in result.lower() else "failed",
                                    "message": result
                                }
                                res_file.seek(0)
                                json.dump(results, res_file, indent=2)
                                print("✅ Result saved to results.json")  # 新增终端输出
                        except json.JSONDecodeError:
                            continue
                last_size = curr_size
        except FileNotFoundError:
            pass
        await asyncio.sleep(1)

from datetime import datetime

async def persistent_service():
    """持久化服务主循环"""
    async with AsyncExitStack() as stack:
        # 初始化并保持MCP连接
        session = await init_mcp_client("scripts/run_server.py", stack)
        await session.initialize()
        print("✅ MCP persistent connection established")
        print("📁 Watching instruction queue file...")

        try:
            await watch_instruction_file(session)
        except asyncio.CancelledError:
            print("🚦 Service shutdown requested")
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")

async def get_llm_instruction() -> dict:
    """从LLM获取单条指令(模拟实现)"""
    # 实际生产环境替换为真正的LLM接口调用
    while True:
        try:
            data = input("Enter LLM instruction (or 'exit' to quit): ")
            if data.lower() == 'exit':
                raise asyncio.CancelledError
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {str(e)}")
            print("Example valid format:")
            print('{"text":"OK","type":"tool","name":"switch_device","arguments":{"device_id":"living_room_tv","status":"on"}}')

async def main():
    """启动持久化服务"""
    try:
        await persistent_service()
    except KeyboardInterrupt:
        print("\n🔴 Service stopped by user")
    except Exception as e:
        print(f"🔴 Unexpected error: {str(e)}")
    finally:
        await shutdown()

async def shutdown():
    # 给资源一些时间关闭
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # 确保所有资源被清理
        asyncio.run(shutdown())
