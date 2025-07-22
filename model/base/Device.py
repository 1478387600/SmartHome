"""
model/base/Device.py - Base device class for smart home system

This module defines the abstract base class for all smart home devices in the system.
It provides common interfaces and functionality that all devices must implement.

Location: model/base/Device.py (relative to project root)
"""

from abc import ABC, abstractmethod

WIDTH = 50
HEIGHT = 50

class Device(ABC):
    """
    Abstract base class for all smart home devices, defining common interfaces.
    """
    _devices = {}  # Class-level registry of all device instances

    def __init__(self, name: str, width=WIDTH, height=HEIGHT, **kwargs):
        """
        Initialize a new device instance.
        
        Args:
            name (str): Unique name identifier for the device
            width (int): Display width in pixels (default: 50)
            height (int): Display height in pixels (default: 50)
            **kwargs: Additional device-specific attributes
        """
        self.name = name
        self.width = width
        self.height = height
        self.__class__._devices[name] = self
        self._canvas_items = {}  # Stores canvas elements for later updates
        self._kwargs = kwargs  # Additional device attributes

    def to_dict(self):
        """
        Convert device object to dictionary representation.
        
        Returns:
            dict: Contains device name, type, and any additional attributes
        """
        data = {
            "name": self.name,
            "type": self.__class__.__name__  # Device type for identification
        }
        data.update(self._kwargs)  # Add any additional attributes
        return data

    @classmethod
    def from_dict(cls, data):
        """
        Reconstruct device object from dictionary data.
        
        Args:
            data (dict): Dictionary containing device attributes
            
        Returns:
            Device: New instance initialized with the provided data
        """
        instance = cls(data["name"], **{k: v for k, v in data.items() if k not in ["name","type"]})
        return instance

    @abstractmethod
    def turn_on(self):
        """
        Turn the device on.
        Must be implemented by all concrete device classes.
        """
        pass

    @abstractmethod
    def turn_off(self):
        """
        Turn the device off.
        Must be implemented by all concrete device classes.
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Get current status of the device.
        
        Returns:
            str: Human-readable status description
        """
        pass

    @classmethod
    def get_status(cls, device_id: str) -> str:
        """
        Get status of a device by its ID.
        
        Args:
            device_id (str): Unique identifier of the device
            
        Returns:
            str: Current status of the device
            
        Raises:
            ValueError: If device with given ID is not found
        """
        device = cls._devices.get(device_id)
        if device:
            return device.get_status()
        raise ValueError(f"Device {device_id} not found")

    def set_level(self, level: int):
        """
        Set device level/intensity (for dimming, opening percentage etc.)
        
        Args:
            level (int): New level value (0-100 typically)
            
        Raises:
            NotImplementedError: If device doesn't support level control
        """
        raise NotImplementedError("Level control not supported by this device")
    
    def draw(self, canvas, x=None, y=None, image=None):
        """
        Draw the device on a canvas including image and status text.
        
        Args:
            canvas: The canvas widget to draw on
            x (int): Optional x-coordinate for center position
            y (int): Optional y-coordinate for center position 
            image: Optional image to use for device representation
        """
        if x is not None:
            self.centreX = x
        if y is not None:
            self.centreY = y
        if image is not None:
            self.image = image

        x1 = self.centreX - self.width // 2
        y1 = self.centreY - self.height // 2
        x2 = self.centreX + self.width // 2
        y2 = self.centreY + self.height // 2

        # Clear previous drawing if exists (to prevent overlapping)
        if self._canvas_items:
            for item in self._canvas_items.values():
                canvas.delete(item)
            self._canvas_items.clear()

        # Draw device image
        if self.image:
            img_item = canvas.create_image(self.centreX, self.centreY, image=self.image, tags=self.name)
        else:
            img_item = canvas.create_rectangle(x1, y1, x2, y2, fill="gray", tags=self.name)

        # Draw status text
        status_text = self.get_status()  # Get status string from concrete implementation
        text_item = canvas.create_text(self.centreX + self.width, 
                                       self.centreY, 
                                       text=status_text, 
                                       tags="appliance_status",
                                       anchor="w", 
                                       font=("Arial", 10))
        # Store canvas items for later updates
        self._canvas_items['image'] = img_item
        self._canvas_items['text'] = text_item
