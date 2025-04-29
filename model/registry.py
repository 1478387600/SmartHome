import os
from typing import Dict
from model.base.Device import Device
from model.base.Sensor import Sensor
from model.Manager.DeviceManager import DeviceManager
from model.Manager.SensorManager import SensorManager

def register_device(device: Device):
    """兼容性函数，设备现在由Device类自身管理"""
    pass

def register_sensor(sensor: Sensor):
    """兼容性函数，传感器现在由Sensor类自身管理"""
    pass

def get_device_by_id(name: str) -> Device:
    """按名称获取设备"""
    device_manager = DeviceManager()
    # print(f"device: {device_manager._devices[name]}")
    # 定义文件路径
    file_path = os.path.join(os.getcwd(), "output.txt")

    # 要写入的内容
    content = device_manager._devices[name]

    # 打开文件并写入内容
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    return device_manager._devices[name]

def get_sensor_by_id(name: str) -> Sensor:
    """按名称获取传感器"""
    sensors_manager = SensorManager()
    return sensors_manager._sensors[name]

def list_all_devices() -> list[str]:
    """列出所有注册设备名"""
    device_manager = DeviceManager()
    return list(device_manager._devices.keys())

def list_all_sensors() -> list[str]:
    """列出所有传感器名"""
    sensors_manager = SensorManager()
    return list(sensors_manager._sensors.keys())
