"""
model/devices/AirConditioner.py - Air Conditioner device implementation

This module implements the AirConditioner class which represents a smart air conditioner
device in the smart home system. It inherits from the base Device class and provides
temperature control functionality.

Location: model/devices/AirConditioner.py (relative to project root)
"""

from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class AirConditioner(Device):
    """
    Air Conditioner device class supporting on/off control and temperature settings.
    """

    def __init__(self, name: str, width=50, height=50, is_on=False, temperature=26, **kwargs):
        """
        Initialize a new AirConditioner instance.
        
        Args:
            name (str): Unique name identifier for the device
            width (int): Display width in pixels (default: 50)
            height (int): Display height in pixels (default: 50) 
            is_on (bool): Initial power state (default: False)
            temperature (int): Initial temperature setting in °C (default: 26)
            **kwargs: Additional device-specific attributes
        """
        super().__init__(name, width, height, **kwargs)
        self.is_on = is_on  # Current power state (True=on, False=off)
        self.temperature = temperature  # Current temperature setting in °C
        DeviceManager.register_device(self)  # Register with device manager

    def to_dict(self):
        """
        Convert device state to dictionary representation.
        
        Returns:
            dict: Contains device state including:
                - Base device attributes (from parent class)
                - is_on: Current power state
                - temperature: Current temperature setting
        """
        data = super().to_dict()  # Get base device attributes
        data["is_on"] = self.is_on  # Add power state
        data["temperature"] = self.temperature  # Add temperature setting
        return data

    @classmethod
    def from_dict(cls, data):
        """
        Reconstruct device instance from dictionary data.
        
        Args:
            data (dict): Dictionary containing device state
            
        Returns:
            AirConditioner: New instance initialized with the provided data
        """
        instance = super().from_dict(data)  # Initialize base device
        instance.is_on = data["is_on"]  # Restore power state
        instance.temperature = data["temperature"]  # Restore temperature setting
        return instance

    def turn_on(self):
        """
        Turn on the air conditioner.
        
        Sets the device's power state to True.
        """
        self.is_on = True

    def turn_off(self):
        """
        Turn off the air conditioner.
        
        Sets the device's power state to False.
        """
        self.is_on = False

    def get_status(self) -> str:
        """
        Get current status of the air conditioner.
        
        Returns:
            str: Human-readable status string including:
                - Power state (on/off)
                - Current temperature setting
        """
        status = "on" if self.is_on else "off"
        return f"{status} at {self.temperature}°C"

    def set_level(self, temp: float):
        """
        Set the air conditioner temperature.
        
        Args:
            temp (float): Desired temperature in °C (16.0-30.0)
            
        Raises:
            ValueError: If temperature is outside valid range
        """
        if 16.0 <= temp <= 30.0:
            self.temperature = temp
        else:
            raise ValueError("Temperature must be between 16°C and 30°C")
