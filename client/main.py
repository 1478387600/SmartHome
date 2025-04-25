import asyncio
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import FileUrl
import subprocess

# 加载环境变量，例如 OPENAI_API_KEY、OPENAI_MODEL 等
load_dotenv()


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI()

    async def connect_to_server(self):
        """连接 MCP 服务器并初始化 session"""
        print("🔌 正在连接到 MCP 服务器...")
        server_params = StdioServerParameters(
            command='uv',
            args=['run', 'server/app.py'],
            env=None
        )

        # 建立与服务器的标准输入输出连接
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params))
        stdio, write = stdio_transport

        # 初始化客户端会话
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write))
        await self.session.initialize()
        print("✅ MCP 客户端会话已初始化。")

    async def process_query(self, query: str) -> str:
        """
        处理用户查询：处理 LLM 的多次工具调用直到生成最终用户响应
        """
        print(f"🧠 正在处理用户查询：{query}")

        system_prompt = (
            "You are a smart home assistant. User queries are meant to control various home devices.\n"
            "Your responses are divided into two typs, answers and tool calls. An answer contain only natural language while tool calls don't.\n"
            "You MUST use provided tool functions to perform actions instead of answering directly.\n"
            "Always preserve the full intent of the user query and respond with the appropriate tool call.\n"
            "If you still want to call the tools, set the finish_reason='tool_calls'.\n"
            "If you are calling a tool in your response while the finish_reason='stop', change it to finish_reason='tool_calls'.\n"
            "If your response is based on tool calls, make sure put all the calls into one response and set the finish_reason='tool_calls'.\n"
            "Your response can not be an answer before you have done all the tool calls need to finish your task given by user."
            "Put multiple tasks in one response using several tool calls.\n"
            "If the user mentions a specific device ID (e.g., bedroom_ac or kitchen_light), use the corresponding tool.\n"
            "NEVER hardcode responses or insert specific time/status values—retrieve them via tool calls.\n"
            "The user might say things like 'turn on living room TV', 'set bedroom AC to 24 degrees', or 'what’s the status of the kitchen light?'—you must respond by calling the correct function.\n"
            "For those devices can be set the values, you put all the arguments in one function call. for example {'device_id': 'living_room_ac', 'status': 'on', 'level': 20} \n"
            "Do not lose user context. Preserve the full query meaning as much as possible.\n"
            "available tools and devices are below\n"
        )

        # 获取当前 MCP 服务器支持的工具
        print("🛠️ 正在请求工具列表...")
        response = await self.session.list_tools()
        print(f"🧰 可用工具：{[tool.name for tool in response.tools]}")

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]

        # 获取设备和传感器列表
        response= await self.session.read_resource("file://devices")
        # print(f"🏡 设备列表：{response.contents[0].text}")
        data = json.loads(str(response.contents[0].text))
        devices = data[0]['content']['devices']
        sensors = data[1]['content']['sensors']
        # 创建包含设备和传感器的 id 和 status 的字典列表
        available_devices = [{"id": device["id"], "status": device["status"]} for device in devices]
        available_sensors = [{"id": sensor["id"], "status": sensor["status"]} for sensor in sensors]

        messages = [
            {"role": "system", "content": system_prompt+str(available_tools)+str(available_devices+available_sensors)},
            {"role": "user", "content": query}
        ]
        # print(f"💬 messages：{messages}")

        # 请求大模型
        print("🤖 正在调用大模型生成工具调用...")
        response = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            tools=available_tools,
        )
        print(f"🗣️ LLM 响应：{response}")

        content = response.choices[0]
        tool_calls = []

        # 检查 LLM 响应中的工具调用
        if content.finish_reason == "tool_calls":
            tool_calls = content.message.tool_calls  # 获取工具调用列表
            messages.append({
                "role": "assistant",
                "tool_calls": [{
                    'id': tool_call.id,
                    'function': {
                        'arguments': tool_call.function.arguments,
                        'name': tool_call.function.name
                    },
                    'type': 'function'
                } for tool_call in tool_calls]
            })

            # 继续调用工具
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"📞 LLM 要调用工具：{tool_name}，参数：{tool_args}")

                # 执行工具调用
                result = await self.session.call_tool(tool_name, tool_args)
                tool_response = ', '.join([
                    item if isinstance(item, str) else getattr(item, 'text', 'No response')
                    for item in result.content
                ]) or "No response"
                print(f"✅ 工具调用完成，返回：{tool_response}")

                # 将工具调用的结果加入消息列表
                messages.append({
                    "role": "tool",
                    "content": tool_response,
                    "tool_call_id": tool_call.id,
                })
                # print(f"✅ 工具调用的结果加入消息列表：{messages}")

            # 继续请求 LLM 生成新的响应
            print("🧠 再次调用大模型以生成新的自然语言响应...")
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
                # tools=available_tools,
            )
            print(f"🗣️ LLM 响应：{response.choices[0]}")

            content = response.choices[0]

        if content.finish_reason == "stop":
            # print(f"🗣️ LLM 最终响应：{content.message.content}")
            return content.message.content
        else:
            # 如果没有返回最终响应，则继续处理
            return await self.process_query(query)

    async def chat_loop(self):
        """主循环，持续接收用户输入并交互"""
        print("💬 进入对话循环，输入 'quit' 可退出")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n🔊 回复：", response)
            except Exception as e:
                import traceback
                print("❌ 出错啦：")
                traceback.print_exc()

    async def cleanup(self):
        """释放资源"""
        print("🧹 正在清理资源...")
        await self.exit_stack.aclose()
        print("🧼 清理完成。")


async def main():
    """程序主入口"""
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys
    result = subprocess.run(['python', 'server/app.py'], capture_output=True, text=True)
    asyncio.run(main())
