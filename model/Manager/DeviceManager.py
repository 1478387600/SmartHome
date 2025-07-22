"""
model/Manager/DeviceManager.py - Core device management for smart home system

This module implements the central device management system for the smart home,
using singleton pattern to ensure global device state consistency. It handles
device registration, state maintenance and access control, providing core device
management capabilities for upper layer services.

Key Features:
- register_device: Register new devices to the system
- get_device_status: Get current status of specified device
- Singleton pattern: Ensures single global instance

Location: model/Manager/DeviceManager.py (relative to project root)

Dependencies:
- model.base.Device: Base device interface definitions
"""

from typing import Dict
from ..base.Device import Device


class DeviceManager:
    """
    Singleton class for device management, providing core functionality for device
    registration and status querying.

    Features:
    - Singleton pattern: Ensures single instance via __new__ override
    - Device registry: Maintains mapping of device names to device objects
    - Status management: Provides unified device status query interface

    Typical usage:
    >>> manager = DeviceManager()
    >>> manager.register_device(Light("living_room_light"))
    >>> print(manager.get_status("living_room_light"))
    """

    _instance = None  # Stores the singleton instance
    _devices: Dict[str, Device] = {}  # Device registry (name -> device object mapping)

    def __new__(cls):
        """
        Singleton constructor ensuring only one instance is created.

        Returns:
            DeviceManager: The single global device manager instance
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_device(cls, device: Device) -> None:
        """
        Register a device with the management system.

        Args:
            device (Device): Device object to register, must implement Device interface

        Note:
            Currently allows duplicate device names (commented out check)
        """
        # if device.name in cls._devices:
        #     raise ValueError(f"Device {device.name} already registered")
        cls._devices[device.name] = device

    @classmethod
    def get_device_status(cls, device_id: str) -> str:
        """
        Get current status of a registered device.

        Args:
            device_id (str): Unique identifier of the device

        Returns:
            str: Human-readable status information

        Raises:
            ValueError: If device is not registered
        """
        device = cls._devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        return device.get_status()
