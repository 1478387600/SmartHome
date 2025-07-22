"""
model/registry.py - Device and sensor registry utilities

This module provides utility functions for managing device and sensor registration
and lookup in the smart home system. It serves as a compatibility layer between
older code and the newer DeviceManager/SensorManager classes.

Location: model/registry.py (relative to project root)
"""

import os
from typing import Dict
from model.base.Device import Device
from model.base.Sensor import Sensor
from model.Manager.DeviceManager import DeviceManager
from model.Manager.SensorManager import SensorManager

def register_device(device: Device):
    """
    Compatibility function - devices are now managed by Device class itself.
    
    Note: This is kept for backward compatibility with older code.
    """
    pass

def register_sensor(sensor: Sensor):
    """
    Compatibility function - sensors are now managed by Sensor class itself.
    
    Note: This is kept for backward compatibility with older code.
    """
    pass

def get_device_by_id(name: str) -> Device:
    """
    Get a device by its unique name identifier.
    
    Args:
        name (str): Unique name of the device to retrieve
        
    Returns:
        Device: The requested device instance
        
    Note:
        Will raise KeyError if device is not found (accessing dict directly)
    """
    device_manager = DeviceManager()
    # print(f"device: {device_manager._devices[name]}")

    # file_path = os.path.join(os.getcwd(), "output.txt")
    # content = device_manager._devices[name]
    # with open(file_path, "a", encoding="utf-8") as file:
    #     file.write(content)

    return device_manager._devices[name]

def get_sensor_by_id(name: str) -> Sensor:
    """
    Get a sensor by its unique name identifier.
    
    Args:
        name (str): Unique name of the sensor to retrieve
        
    Returns:
        Sensor: The requested sensor instance
        
    Note:
        Will raise KeyError if sensor is not found (accessing dict directly)
    """
    sensors_manager = SensorManager()
    return sensors_manager._sensors[name]

def list_all_devices() -> list[str]:
    """
    Get names of all registered devices.
    
    Returns:
        list[str]: List of all device names in the system
    """
    device_manager = DeviceManager()
    return list(device_manager._devices.keys())

def list_all_sensors() -> list[str]:
    """
    Get names of all registered sensors.
    
    Returns:
        list[str]: List of all sensor names in the system
    """
    sensors_manager = SensorManager()
    return list(sensors_manager._sensors.keys())
