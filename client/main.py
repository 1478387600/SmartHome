"""
client/main.py - MCP Client Main Entry Point

This module implements the main client interface for the Model Context Protocol (MCP)
smart home system. It handles communication with the MCP server and coordinates
LLM-powered device control through tool calls.

Key Features:
- MCP server connection management
- LLM-powered query processing
- Tool call execution
- Interactive chat interface

Location: client/main.py (relative to project root)

Dependencies:
- mcp: MCP protocol implementation
- openai: OpenAI API client
- dotenv: Environment variable management
"""

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

# Load environment variables (OPENAI_API_KEY, OPENAI_MODEL etc.)
load_dotenv()


class MCPClient:
    """
    Main client class for MCP smart home system.
    
    Handles:
    - Server connection management
    - LLM-powered query processing
    - Tool call execution
    - Resource cleanup
    
    Attributes:
        session: Active MCP client session
        exit_stack: Async resource manager
        client: OpenAI client instance
    """
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI()

    async def connect_to_server(self):
        """
        Establish connection to MCP server and initialize session.
        
        Uses stdio transport to communicate with server process.
        Prints connection status messages.
        
        Raises:
            ConnectionError: If server connection fails
        """
        print("🔌 Connecting to MCP server...")
        server_params = StdioServerParameters(
            command='uv',
            args=['run', 'server/app.py'],
            env=None
        )

        # Establish stdio connection with server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params))
        stdio, write = stdio_transport

        # Initialize client session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write))
        await self.session.initialize()
        print("✅ MCP client session initialized")

    async def process_query(self, query: str) -> str:
        """
        Process user query through LLM tool calls to generate final response.
        
        Args:
            query: User input string to process
            
        Returns:
            str: Final natural language response after executing all tool calls
            
        Steps:
            1. Setup system prompt with tool usage instructions
            2. Get available tools from MCP server
            3. Get device/sensor status lists
            4. Call LLM to generate tool calls
            5. Execute tool calls and collect results
            6. Get final natural language response from LLM
        """
        print(f"🧠 Processing user query: {query}")

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

        # Get available tools from MCP server
        print("🛠️ Requesting tool list...")
        response = await self.session.list_tools()
        print(f"🧰 Available tools: {[tool.name for tool in response.tools]}")

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]

        # Get device and sensor lists from MCP server
        response = await self.session.read_resource("file://devices")
        # print(f"🏡 Device list: {response.contents[0].text}")
        data = json.loads(str(response.contents[0].text))
        devices = data[0]['content']['devices']
        sensors = data[1]['content']['sensors']
        # Create dictionaries with device/sensor IDs and statuses
        available_devices = [{"id": device["id"], "status": device["status"]} for device in devices]
        available_sensors = [{"id": sensor["id"], "status": sensor["status"]} for sensor in sensors]

        messages = [
            {"role": "system", "content": system_prompt+str(available_tools)+str(available_devices+available_sensors)},
            {"role": "user", "content": query}
        ]
        # print(f"💬 messages：{messages}")

        # Call LLM to generate tool calls
        print("🤖 Calling LLM to generate tool calls...")
        response = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            tools=available_tools,
        )
        print(f"🗣️ LLM response: {response}")

        content = response.choices[0]
        tool_calls = []

        # Check for tool calls in LLM response
        if content.finish_reason == "tool_calls":
            tool_calls = content.message.tool_calls  # Get list of tool calls
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

            # Execute each tool call
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"📞 LLM requesting tool call: {tool_name}, args: {tool_args}")

                # Execute the tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_response = ', '.join([
                    item if isinstance(item, str) else getattr(item, 'text', 'No response')
                    for item in result.content
                ]) or "No response"
                print(f"✅ Tool call completed, response: {tool_response}")

                # Add tool response to messages
                messages.append({
                    "role": "tool",
                    "content": tool_response,
                    "tool_call_id": tool_call.id,
                })
                # print(f"✅ Tool response added to messages: {messages}")

            # Request final natural language response from LLM
            print("🧠 Requesting final natural language response from LLM...")
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
                # tools=available_tools,
            )
            print(f"🗣️ LLM response: {response.choices[0]}")

            content = response.choices[0]

        if content.finish_reason == "stop":
            # print(f"🗣️ LLM final response: {content.message.content}")
            return content.message.content
        else:
            # If no final response, continue processing
            return await self.process_query(query)

    async def chat_loop(self):
        """
        Main interactive chat loop for processing user queries.
        
        Continuously prompts for user input until 'quit' is entered.
        Handles each query through process_query() and prints responses.
        Shows error details if exceptions occur.
        """
        print("💬 Entering chat loop (type 'quit' to exit)")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n🔊 Response:", response)
            except Exception as e:
                import traceback
                print("❌ Error occurred:")
                traceback.print_exc()

    async def cleanup(self):
        """
        Clean up resources and close connections.
        
        Properly closes the async exit stack which manages:
        - MCP server connection
        - Session resources
        - Any other async resources
        """
        print("🧹 Cleaning up resources...")
        await self.exit_stack.aclose()
        print("🧼 Cleanup completed.")


async def main():
    """
    Main entry point for MCP client application.
    
    Initializes client, connects to server, runs chat loop,
    and ensures proper cleanup on exit.
    """
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
