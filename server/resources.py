"""
MCP 资源读取函数定义模块。

该模块通过 `@mcp.resource()` 向 LLM 提供环境信息读取能力，例如温度、电力消耗、降雨等。
"""

from server.app import mcp
from model.registry import get_sensor_by_id


@mcp.resource("sensor://indoor-temperature")
def get_indoor_temperature() -> str:
    """
    获取室内温度（单位 °C）。

    返回:
        温度字符串，如 "25.3°C"
    """
    sensor = get_sensor_by_id("indoor_temp")
    return f"{sensor.read_value()}°C"


@mcp.resource("sensor://outdoor-temperature")
def get_outdoor_temperature() -> str:
    """
    获取室外温度（单位 °C）。

    返回:
        温度字符串
    """
    sensor = get_sensor_by_id("outdoor_temp")
    return f"{sensor.read_value()}°C"


@mcp.resource("sensor://rain-mm")
def get_rain_mm() -> str:
    """
    获取当前降雨量（单位 mm）。

    返回:
        降雨字符串，如 "3.5mm"
    """
    sensor = get_sensor_by_id("rain_sensor")
    return f"{sensor.read_value()}mm"


@mcp.resource("sensor://power-usage")
def get_power_usage() -> str:
    """
    获取当前耗电功率（单位 W）。

    返回:
        功率字符串，如 "560W"
    """
    sensor = get_sensor_by_id("power_meter")
    return f"{sensor.read_value()}W"
