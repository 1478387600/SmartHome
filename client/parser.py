"""
LLM 响应解析模块。

该模块负责将 LLM 输出的极简 JSON 响应解析成结构化对象，供 MCP 调用器使用。
"""

from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class ParsedLLMResponse:
    """
    结构化后的 LLM 响应格式。

    该类用于将 LLM 返回的工具调用或资源请求转化为结构化数据，方便后续的 MCP 调用。
    
    属性：
        type: 响应类型，值为 "tool" 或 "resource"。
        name: 对应的工具名称（如 "switch_device"）或资源名称（如 "sensor://indoor-temperature"）。
        arguments: 工具调用时传递的参数，默认为空字典。
    """
    type: str                 # "tool" 或 "resource"
    name: str                 # toolName 或 resourceName
    arguments: Optional[dict] = None

def parse_llm_response(response_str: str) -> ParsedLLMResponse:
    """
    解析 LLM 响应的 JSON 字符串，并返回结构化后的对象。

    参数：
        response_str (str): LLM 响应的 JSON 字符串。

    返回：
        ParsedLLMResponse: 解析后的结构化对象。
    """
    try:
        # 尝试解析 JSON 字符串
        item = json.loads(response_str)

        if not isinstance(item, dict):
            raise ValueError("Response must be a dictionary")

        if item.get("type") == "tool" and "name" in item:
            return ParsedLLMResponse(
                type="tool",
                name=item["name"],
                arguments=item.get("arguments", {})
            )
        elif item.get("type") == "resource" and "name" in item:
            return ParsedLLMResponse(
                type="resource",
                name=item["name"],
                arguments=item.get("arguments", {})
            )
        else:
            raise ValueError("Invalid LLM response: missing 'name' or 'type'")

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Invalid LLM response: {str(e)}")
