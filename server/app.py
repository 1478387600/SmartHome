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
import multiprocessing
import os
import subprocess
import sys
from multiprocessing import Pipe
from pathlib import Path
import threading
from typing import Optional
import argparse

# from environment.home_simulator import HomeSimulator

# 将项目根目录添加到Python路径（注意：推荐使用包管理方式替代路径修改）
sys.path.append(str(Path(__file__).parent.parent))

# 服务核心组件
# import mcp.types as types
from mcp.types import Resource, FileUrl
from mcp.server import FastMCP
from mcp.server.models import InitializationOptions
import json
from model.registry import get_device_by_id

from model.devices.AirConditioner import AirConditioner
from model.devices.AirPurifier import AirPurifier
from model.devices.Blind import Blind
from model.devices.Curtain import Curtain
from model.devices.Light import Light
from model.devices.TV import TV
from model.devices.Window import Window
from model.sensors.IndoorTempSensor import IndoorTempSensor
from model.sensors.OutdoorTempSensor import OutdoorTempSensor
from model.sensors.PowerMeter import PowerMeter
from model.sensors.RainSensor import RainSensor


# 从标准输入接收 appliances_data（JSON 格式）
# input_data = sys.stdin.read()  # 读取管道传输的全部数据
with open(r'server\resources\mock_appliances_init.txt', 'r', encoding='utf-8') as file:
    input_data = file.read().strip()  # 读取并去除首尾的空白字符
print(input_data,type(input_data))
if input_data:
    appliances_data = json.loads(input_data)
else:
    appliances_data = []


# 反序列化 appliances 数据并根据设备类型创建相应的设备实例
appliances = []
for data in appliances_data:
    print(f"data: {data} {type(data)}")
    device_type = data["type"]  # 获取设备类型
    if device_type == "AirConditioner":
        appliance = AirConditioner.from_dict(data)
    elif device_type == "AirPurifier":
        appliance = AirPurifier.from_dict(data)
    elif device_type == "Blind":
        appliance = Blind.from_dict(data)
    elif device_type == "Curtain":
        appliance = Curtain.from_dict(data)
    elif device_type == "Light":
        appliance = Light.from_dict(data)
    elif device_type == "TV":
        appliance = TV.from_dict(data)
    elif device_type == "Window":
        appliance = Window.from_dict(data)
    elif device_type == "IndoorTempSensor":
        appliance = IndoorTempSensor.from_dict(data)
    elif device_type == "OutdoorTempSensor":
        appliance = OutdoorTempSensor.from_dict(data)
    elif device_type == "PowerMeter":
        appliance = PowerMeter.from_dict(data)
    elif device_type == "RainSensor":
        appliance = RainSensor.from_dict(data)
    else:
        # 如果类型无法识别，跳过或报错
        print(f"Unrecognized device type: {device_type}")
        continue

    appliances.append(appliance)


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resources")
# 预定义资源清单
STATIC_RESOURCES = {
    "devices": {
        "name": "Device List",
        "desc": "预注册设备清单",
        "path": "server/resources/devices.json"
    },
    "sensors": {
        "name": "Sensor List", 
        "desc": "传感器实时状态",
        "path": "server/resources/sensors.json"
    }
}

# 初始化智能家居MCP服务实例
mcp = FastMCP('smart-home')


@mcp.tool()
def control_device(device_id: str, status: str, level: Optional[int] = None) -> str:
    """
    设备控制函数，根据传入的状态控制设备的开关，并可选地设置设备的级别

    参数:
        device_id: 设备唯一标识符，需在设备注册表中存在
        status: 设备目标状态，"on"表示开启，"off"表示关闭
        level: 设备运行参数值，范围0-100的整数百分比，仅在需要调节设备级别时使用

    返回:
        str: 包含操作结果的格式化字符串，示例：
            - "Device light01 turned on"
            - "Device curtain02 set to 75%"
    """

    device = get_device_by_id(device_id)

    file_path = os.path.join(os.getcwd(), "output.txt")
    content = "entered control_device()"
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content)
    
    # 处理设备开关状态
    if status == "on":
        device.turn_on()
        return f"Device {device_id} turned on"
    elif status == "off":
        device.turn_off()
        return f"Device {device_id} turned off"

    # 如果有 level 参数且设备支持调节级别，执行设置级别操作
    if level is not None:
        device.set_level(level)
        return f"Device {device_id} set to {level}"

    return "Invalid status or level parameter"


# @mcp.tool()
# def list_devices() -> list[str]:
#     """
#     获取已注册设备清单
#
#     返回:
#         list[str]: 当前系统中所有注册设备的ID列表
#     """
#     from model.registry import list_all_devices
#     return list_all_devices()

@mcp.tool()
def test_ping() -> str:
    """
    服务健康检查接口

    返回:
        str: 固定响应"pong"用于服务连通性测试
    """
    return "pong"

@mcp.tool()
def get_status(device_id: str) -> dict:
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


@mcp.resource("file://devices")
async def list_resources() -> list[Resource]:
    """返回所有已注册资源的元数据并读取文件内容"""
    resources = []
    for res_id, info in STATIC_RESOURCES.items():
        # 读取文件内容
        file_path = Path(__file__).parent / 'resources' / f'{res_id}.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = json.load(file)

        resources.append(
            Resource(
                uri=FileUrl(f"file://{file_path}"),
                name=info["name"],
                description=info["desc"],
                mime_type="application/json",
                file_path=file_path.resolve(),
                content=file_content  # 返回文件内容
            )
        )
    return resources


def add_resources():
    # 添加设备资源，确保路径指向具体文件
    devices_resource = Resource(
        uri="file://resources/devices.json",  # 使用完整的 URI 路径
        path=Path(__file__).parent / "resources" / "devices.json",  # 使用 Path 动态构建文件路径
        mime_type="application/json",
        name="Device List",
        description="预注册设备清单"
    )
    mcp.add_resource(devices_resource)

    # 添加传感器资源，确保路径指向具体文件
    sensors_resource = Resource(
        uri="file://resources/sensors.json",  # 使用完整的 URI 路径
        path=Path(__file__).parent / "resources" / "sensors.json",  # 使用 Path 动态构建文件路径
        mime_type="application/json",
        name="Sensor List",
        description="传感器实时状态",
        refresh_interval=5  # 5秒刷新间隔
    )
    mcp.add_resource(sensors_resource)

# def initialize_environment(args):
#     # 创建 HomeSimulator 实例并实例化设备
#     simulator = HomeSimulator()
#     appliances = simulator.instantiate_devices()
#
#     # 将 appliances 列表中的每个设备实例转换为字典
#     appliances_data = [device.to_dict() for device in appliances[0]]  # 假设设备有 to_dict 方法
#
#     # 使用 multiprocessing 启动两个进程
#
#     # 进程 2: 启动 sim_main()
#     sim_process = multiprocessing.Process(target=sim_main_process, args=(args, appliances_data))
#     sim_process.start()
#
#     # 等待进程完成
#     sim_process.join()
#
# def sim_main_process(args, appliances_data):
#     from environment.simulator_with_appliance import sim_main
#     numOfRobots, numOfCats, amountOfDirt, timeOfDirt, drawCamLine, drawGrid = args
#     sim_main(numOfRobots, numOfCats, amountOfDirt, timeOfDirt, drawCamLine, drawGrid, appliances_data)


def start_server():
    # 启动 server/app.py
    process = subprocess.Popen(
        ["python", "server/app.py"],
        stdin=subprocess.PIPE,  # 管道输入
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


    # 要传递的设备数据（示例）
    devices_data = []
    for device in appliances:
        devices_data.append(device.to_dict())

    # 将设备数据转为 JSON 格式并通过管道传输
    json_data = json.dumps(devices_data)
    process.stdin.write(json_data.encode())  # 写入数据
    process.stdin.flush()

    # 获取子进程输出（如果有）
    output = process.stdout.read().decode()
    print(output)

    # 等待进程结束
    process.wait()

def main():
    print("launching MCP server subprocess ...")
    mcp.run(transport='stdio')

# 主入口：使用标准输入输出作为通信通道启动MCP服务
if __name__ == "__main__":
    # from .runner import main

    # simulator = HomeSimulator()
    # appliances = simulator.instantiate_devices()
    # simulator.start()
    # args = [1,1,1,3000,False,False]
    # initialize_environment(args)

    # print("launching MCP server subprocess ...")
    # mcp.run(transport='stdio')
    main()
