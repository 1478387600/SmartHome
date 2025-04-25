import asyncio
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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
        处理用户查询：
        1. 构造 system prompt 和 user query
        2. 获取当前可用的工具列表
        3. 向 LLM 发起调用请求（包括 tool schema）
        4. 如果 LLM 返回 tool_call，调用对应的 tool
        5. 将工具结果返回给 LLM 以生成最终响应
        """
        print(f"🧠 正在处理用户查询：{query}")
        system_prompt = (
            "You are a smart home assistant. User queries are meant to control various home devices.\n"
            "You MUST use provided tool functions to perform actions instead of answering directly.\n"
            "Your available tools include: turning devices on/off, setting device parameters (brightness, curtain level, etc.), checking device status, and listing all devices.\n"
            "Always preserve the full intent of the user query and respond with the appropriate tool call.\n"
            "If the user mentions a specific device ID (e.g., bedroom_ac or kitchen_light), use the corresponding tool.\n"
            "NEVER hardcode responses or insert specific time/status values—retrieve them via tool calls.\n"
            "The user might say things like 'turn on living room TV', 'set bedroom AC to 24 degrees', or 'what’s the status of the kitchen light?'—you must respond by calling the correct function.\n"
            "Do not lose user context. Preserve the full query meaning as much as possible."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

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

        # 请求大模型
        print("🤖 正在调用大模型生成工具调用...")
        response = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            tools=available_tools
        )

        content = response.choices[0]

        if content.finish_reason == "tool_calls":
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            print(f"📞 LLM 要调用工具：{tool_name}，参数：{tool_args}")

            # 执行工具调用
            result = await self.session.call_tool(tool_name, tool_args)
            # 带空值保护，将result转为string
            tool_response = ', '.join([
                item if isinstance(item, str) else getattr(item, 'text', '')
                for item in result.content
            ]) or "No response"
            print(f"✅ 工具调用完成，返回：{tool_response}")

            # 构建用于 LLM 的响应上下文
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": tool_response,
                "tool_call_id": tool_call.id,
            })

            # 再次请求 LLM，生成最终用户自然语言响应
            print("🧠 再次调用大模型以生成最终自然语言响应...")
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
            )
            final_response = response.choices[0].message.content
            # print(f"🗣️ LLM 最终响应：{final_response}")
            return final_response

        print(f"🗣️ LLM 未调用工具，直接响应：{content.message.content}")
        return content.message.content

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
    asyncio.run(main())
