from model.base.Sensor import Sensor
import random

class PowerMeter(Sensor):
    """
    电表传感器类。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.unit = "W"

    def read_value(self):
        """读取当前耗电量"""
        return random.randint(100, 5000)  # Random power between 100-5000W
