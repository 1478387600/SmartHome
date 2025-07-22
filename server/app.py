"""
server/app.py - Smart Home Control Service Main Module

This module serves as the core service entry point for the smart home system,
handling device control requests including:
- Turning devices on/off
- Setting device parameters
- Listing registered devices
- Health checking

Built on FastMCP framework, using stdio for client communication.

Key Features:
- Device control via MCP tools
- Resource management for devices/sensors
- Health monitoring endpoints

Location: server/app.py (relative to project root)

Dependencies:
- mcp.types: MCP type definitions
- mcp.server: MCP server framework  
- model.registry: Device registry management
"""
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

# Add project root to Python path (Note: Package management is preferred over path modification)
sys.path.append(str(Path(__file__).parent.parent))

# Core service components
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


# Read appliances data from mock initialization file (JSON format)
# Alternative: input_data = sys.stdin.read()  # Read all piped data
with open(r'server\resources\mock_appliances_init.txt', 'r', encoding='utf-8') as file:
    input_data = file.read().strip()  # Read and strip whitespace
print(input_data,type(input_data))
if input_data:
    appliances_data = json.loads(input_data)
else:
    appliances_data = []


# Deserialize appliances data and create corresponding device instances
appliances = []
for data in appliances_data:
    print(f"data: {data} {type(data)}")
    device_type = data["type"]  # Get device type
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
        # Skip or error if device type is unrecognized
        print(f"Unrecognized device type: {device_type}")
        continue

    appliances.append(appliance)


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), "resources")
# Predefined resource list
STATIC_RESOURCES = {
    "devices": {
        "name": "Device List",
        "desc": "Pre-registered device inventory",
        "path": "server/resources/devices.json"
    },
    "sensors": {
        "name": "Sensor List", 
        "desc": "Real-time sensor status",
        "path": "server/resources/sensors.json"
    }
}

# Initialize smart home MCP service instance
mcp = FastMCP('smart-home')


@mcp.tool()
def control_device(device_id: str, status: str, level: Optional[int] = None) -> str:
    """
    Control a device by changing its power state and optionally setting its level.

    Args:
        device_id: Unique device identifier (must exist in registry)
        status: Target power state ("on" to turn on, "off" to turn off)
        level: Optional parameter value (0-100 integer percentage) for devices
               that support level control

    Returns:
        str: Formatted result string, examples:
            - "Device light01 turned on"
            - "Device curtain02 set to 75%"
            
    Raises:
        ValueError: If device_id is not found in registry
    """

    device = get_device_by_id(device_id)
    
    # Handle device power state
    if status == "on":
        device.turn_on()
        return f"Device {device_id} turned on"
    elif status == "off":
        device.turn_off()
        return f"Device {device_id} turned off"

    # If level parameter is provided and device supports level control
    if level is not None:
        device.set_level(level)
        return f"Device {device_id} set to {level}"

    return "Invalid status or level parameter"


# @mcp.tool()
# def list_devices() -> list[str]:
#     """
#     Get list of all registered devices
#
#     Returns:
#         list[str]: IDs of all registered devices in the system
#     """
#     from model.registry import list_all_devices
#     return list_all_devices()

@mcp.tool()
def test_ping() -> str:
    """
    Health check endpoint for service connectivity testing.

    Returns:
        str: Constant "pong" response to verify service is running
    """
    return "pong"

@mcp.tool()
def get_status(device_id: str) -> dict:
    """
    Get current status of a device or sensor.
    
    Args:
        device_id: Unique identifier of the device/sensor
        
    Returns:
        dict: Status object containing:
            - id: Device/sensor ID
            - type: "device" or "sensor"
            - status: Current state information
            - timestamp: ISO format timestamp
            
    Note:
        Returns error object if device_id is not found
    """
    from model.Manager.DeviceManager import DeviceManager
    from model.Manager.SensorManager import SensorManager
    from datetime import datetime
    
    if not device_id:
        return {
            "error": "Device ID is required",
            "timestamp": datetime.now().isoformat()
        }
    
    # Try to get as device
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
    
    # Try to get as sensor
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
    """
    List all registered resources and read their file contents.
    
    Returns:
        list[Resource]: List of Resource objects containing:
            - URI
            - Name
            - Description
            - MIME type
            - File path
            - File content
    """
    resources = []
    for res_id, info in STATIC_RESOURCES.items():
        # Read file content
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
                content=file_content  # Return file content
            )
        )
    return resources


def add_resources():
    """
    Add static resources to the MCP server.
    
    Registers two main resources:
    - devices.json: Pre-registered device list
    - sensors.json: Real-time sensor status
    
    Note:
        Resources are configured with refresh intervals and metadata
    """
    # Add device resource with specific file path
    devices_resource = Resource(
        uri="file://resources/devices.json",  # Full URI path
        path=Path(__file__).parent / "resources" / "devices.json",  # Dynamic file path construction
        mime_type="application/json",
        name="Device List",
        description="Pre-registered device inventory"
    )
    mcp.add_resource(devices_resource)

    # Add sensor resource with specific file path
    sensors_resource = Resource(
        uri="file://resources/sensors.json",  # Full URI path
        path=Path(__file__).parent / "resources" / "sensors.json",  # Dynamic file path construction
        mime_type="application/json",
        name="Sensor List",
        description="Real-time sensor status",
        refresh_interval=5  # 5 second refresh interval
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
    # Start server/app.py subprocess
    process = subprocess.Popen(
        ["python", "server/app.py"],
        stdin=subprocess.PIPE,  # Pipe input
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Prepare device data to pass (example)
    devices_data = []
    for device in appliances:
        devices_data.append(device.to_dict())

    # Convert device data to JSON and pipe it
    json_data = json.dumps(devices_data)
    process.stdin.write(json_data.encode())  # Write data
    process.stdin.flush()

    # Get subprocess output (if any)
    output = process.stdout.read().decode()
    print(output)

    # Wait for process to complete
    process.wait()

def main():
    print("launching MCP server subprocess ...")
    mcp.run(transport='stdio')

# Main entry: Start MCP service using stdio for communication
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
