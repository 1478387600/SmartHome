"""
model/base/Sensor.py - Base sensor class for smart home system

This module defines the abstract base class for all smart home sensors in the system.
It provides common interfaces and functionality that all sensors must implement.

Location: model/base/Sensor.py (relative to project root)
"""

from abc import ABC, abstractmethod

WIDTH = 50
HEIGHT = 50

class Sensor(ABC):
    """
    Abstract base class for all smart home sensors, defining common interfaces.
    """
    _sensors = {}  # Class-level registry of all sensor instances

    def __init__(self, name: str, width=WIDTH, height=HEIGHT, **kwargs):
        """
        Initialize a new sensor instance.
        
        Args:
            name (str): Unique name identifier for the sensor
            width (int): Display width in pixels (default: 50)
            height (int): Display height in pixels (default: 50)
            **kwargs: Additional sensor-specific attributes
        """
        self.name = name
        self.width = width
        self.height = height
        self.__class__._sensors[name] = self
        self._canvas_items = {}  # Stores canvas elements for later updates
        self._kwargs = kwargs

    def to_dict(self):
        """
        Convert sensor object to dictionary representation.
        
        Returns:
            dict: Contains sensor name and type
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__  # Sensor type for identification
        }

    @classmethod
    def from_dict(cls, data):
        """
        Reconstruct sensor object from dictionary data.
        
        Args:
            data (dict): Dictionary containing sensor attributes
            
        Returns:
            Sensor: New instance initialized with the provided data
        """
        instance = cls(data["name"], **{k: v for k, v in data.items() if k not in ["name","type"]})
        return instance


    @abstractmethod
    def read_value(cls, device_id: str):
        """
        Read current value from sensor by device ID.
        
        Args:
            device_id (str): Unique identifier of the sensor
            
        Returns:
            Any: Current sensor reading value
            
        Raises:
            ValueError: If sensor with given ID is not found
        """
        sensor = cls._sensors.get(device_id)
        if sensor:
            return sensor.get_status()
        raise ValueError(f"Sensor {device_id} not found")
    
    def draw(self, canvas, x=None, y=None, image=None):
        """
        Draw the sensor on a canvas including image and status text.
        
        Args:
            canvas: The canvas widget to draw on
            x (int): Optional x-coordinate for center position
            y (int): Optional y-coordinate for center position 
            image: Optional image to use for sensor representation
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

        # Draw sensor image
        if self.image:
            img_item = canvas.create_image(self.centreX, self.centreY, image=self.image, tags=self.name)
        else:
            img_item = canvas.create_rectangle(x1, y1, x2, y2, fill="gray", tags=self.name)

        # Draw status text
        status_text = self.read_value()  # Get status string from concrete implementation
        text_item = canvas.create_text(self.centreX + self.width, 
                                       self.centreY, 
                                       text=status_text, 
                                       tags="appliance_status",
                                       anchor="w", 
                                       font=("Arial", 10))
        # Store canvas items for later updates
        self._canvas_items['image'] = img_item
        self._canvas_items['text'] = text_item
