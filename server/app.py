""" 
智能家居设备控制服务主模块

该模块是智能家居系统的核心服务入口，负责处理设备控制请求，包括开关设备、设置设备级别、列出设备列表等功能。

模块基于 FastMCP 框架实现，通过标准输入输出与客户端进行通信。

模块功能：
- switch_device: 控制设备的开关状态
- set_device_level: 设置设备的运行参数值
- list_devices: 获取已注册设备的ID列表
- test_ping: 服务健康检查接口

项目位置：
- 模块路径: server/app.py 

依赖模块：
- mcp.types: MCP 类型定义
- mcp.server: MCP 服务框架
- model.registry: 设备注册表管理"""

import sys
from pathlib import Path

# 将项目根目录添加到Python路径（注意：推荐使用包管理方式替代路径修改）
sys.path.append(str(Path(__file__).parent.parent))

# 服务核心组件
import mcp.types as types
from mcp.server import FastMCP
from mcp.server.models import InitializationOptions
from model.registry import get_device_by_id
from environment.simulator import instantiate_home_devices

# 初始化智能家居MCP服务实例
mcp = FastMCP('smart-home')

@mcp.tool()
def switch_device(device_id: str, status: str) -> str:
    """
    设备开关控制函数

    参数:
        device_id: 设备唯一标识符，需在设备注册表中存在
        status: 设备目标状态，"on"表示开启，"off"表示关闭

    返回:
        str: 包含操作结果的格式化字符串，示例："Device light01 turned on"
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
    设备数值调节函数

    参数:
        device_id: 支持级别控制的设备ID（如调光灯、窗帘电机等）
        level: 设备运行参数值，范围0-100的整数百分比

    返回:
        str: 包含设置结果的格式化字符串，示例："Device curtain02 set to 75%"
    """
    device = get_device_by_id(device_id)
    device.set_level(level)
    return f"Device {device_id} set to {level}%"

@mcp.tool()
def list_devices() -> list[str]:
    """
    获取已注册设备清单

    返回:
        list[str]: 当前系统中所有注册设备的ID列表
    """
    from model.registry import list_all_devices
    return list_all_devices()

@mcp.tool()
def test_ping() -> str:
    """
    服务健康检查接口

    返回:
        str: 固定响应"pong"用于服务连通性测试
    """
    return "pong"

@mcp.tool()
def get_device_status(device_id: str) -> dict:
    """
    获取设备状态
    
    参数:
        device_id: 设备ID
        
    返回:
        dict: {
            "id": str,
            "type": "device"|"sensor",
            "status": Any,
            "timestamp": str(ISO格式)
        }
    """
    from model.Manager.DeviceManager import DeviceManager
    from model.Manager.SensorManager import SensorManager
    from datetime import datetime
    
    if not device_id:
        return {
            "error": "Device ID is required",
            "timestamp": datetime.now().isoformat()
        }
    
    # 尝试作为设备获取
    device_manager = DeviceManager()
    if device_id in device_manager._devices:
        try:
            status = device_manager.get_device_status(device_id)
            return {
                "id": device_id,
                "type": "device",
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        except ValueError:
            pass
    
    # 尝试作为传感器获取
    sensor_manager = SensorManager()
    if device_id in sensor_manager._sensors:
        try:
            status = sensor_manager.get_sensor_status(device_id)
            return {
                "id": device_id,
                "type": "sensor", 
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        except ValueError:
            pass
    
    return {
        "error": f"No device/sensor found with ID: {device_id}",
        "timestamp": datetime.now().isoformat()
    }

# 主入口：使用标准输入输出作为通信通道启动MCP服务
if __name__ == "__main__":
    print(instantiate_home_devices())
    # 启动MCP服务
    mcp.run(transport='stdio')
    print("MCP server subprocess launched.")
