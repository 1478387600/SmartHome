from model.base.Sensor import Sensor
from model.Manager.SensorManager import SensorManager
import random

class PowerMeter(Sensor):
    """
    电表传感器类。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.unit = "W"
        SensorManager.register_sensor(self)

    def read_value(self):
        """读取当前耗电量"""
        return random.randint(100, 5000)  # Random power between 100-5000W
