from abc import ABC, abstractmethod

class Sensor(ABC):
    """
    所有传感器类型的抽象基类。
    """
    _sensors = {}

    def __init__(self, name: str):
        self.name = name
        self.__class__._sensors[name] = self

    @abstractmethod
    def read_value(cls, device_id: str):
        """读取当前传感器值"""
        sensor = cls._sensors.get(device_id)
        if sensor:
            return sensor.get_status()
        raise ValueError(f"Sensor {device_id} not found")
