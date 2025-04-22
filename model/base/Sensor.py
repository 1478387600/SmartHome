from abc import ABC, abstractmethod

class Sensor(ABC):
    """
    所有传感器类型的抽象基类。
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def read_value(self):
        """读取当前传感器值"""
        pass
