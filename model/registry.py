from typing import Dict
from model.base.Device import Device
from model.base.Sensor import Sensor

def register_device(device: Device):
    """兼容性函数，设备现在由Device类自身管理"""
    pass

def register_sensor(sensor: Sensor):
    """兼容性函数，传感器现在由Sensor类自身管理"""
    pass

def get_device_by_id(name: str) -> Device:
    """按名称获取设备"""
    return Device._devices[name]

def get_sensor_by_id(name: str) -> Sensor:
    """按名称获取传感器"""
    return Sensor._sensors[name]

def list_all_devices() -> list[str]:
    """列出所有注册设备名"""
    return list(Device._devices.keys())

def list_all_sensors() -> list[str]:
    """列出所有传感器名"""
    return list(Sensor._sensors.keys())
