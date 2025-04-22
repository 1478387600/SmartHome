from typing import Dict
from model.base.Device import Device
from model.base.Sensor import Sensor

# 全局注册表
device_registry: Dict[str, Device] = {}
sensor_registry: Dict[str, Sensor] = {}

def register_device(device: Device):
    """将设备注册到全局字典中"""
    device_registry[device.name] = device

def register_sensor(sensor: Sensor):
    """将传感器注册到全局字典中"""
    sensor_registry[sensor.name] = sensor

def get_device_by_id(name: str) -> Device:
    """按名称获取设备"""
    return device_registry[name]

def get_sensor_by_id(name: str) -> Sensor:
    """按名称获取传感器"""
    return sensor_registry[name]

def list_all_devices() -> list[str]:
    """列出所有注册设备名"""
    return list(device_registry.keys())

def list_all_sensors() -> list[str]:
    """列出所有传感器名"""
    return list(sensor_registry.keys())
