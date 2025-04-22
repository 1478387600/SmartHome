"""
MCP 工具函数定义模块。

该模块通过 `@mcp.tool()` 装饰器向 LLM 暴露可调用的设备控制操作，例如开关设备、调整亮度或设定级别。
"""

from server.app import mcp
from model.registry import get_device_by_id


@mcp.tool()
def switch_device(device_id: str, status: str) -> str:
    """
    打开或关闭指定设备。

    参数:
        device_id: 注册的设备名称
        status: "on" 或 "off"

    返回:
        操作结果描述字符串
    """
    device = get_device_by_id(device_id)
    if status == "on":
        device.turn_on()
    else:
        device.turn_off()
    return f"Device {device_id} turned {status}"


@mcp.tool()
def set_device_level(device_id: str, level: int) -> str:
    """
    设置设备的数值级别（如亮度、开合度）。

    参数:
        device_id: 设备ID
        level: 整数百分比 0-100

    返回:
        设置结果描述字符串
    """
    device = get_device_by_id(device_id)
    device.set_level(level)
    return f"Device {device_id} set to {level}%"


@mcp.tool()
def list_devices() -> list[str]:
    """
    返回所有已注册设备的名称列表。

    返回:
        字符串列表
    """
    from model.registry import list_all_devices
    return list_all_devices()

@mcp.tool()
def test_ping() -> str:
    return "pong"
