from model.base.Sensor import Sensor
from model.Manager.SensorManager import SensorManager
import random

class RainSensor(Sensor):
    """
    降雨量传感器类。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.unit = "mm"
        SensorManager.register_sensor(self)

    def read_value(self):
        """读取当前降雨量"""
        return round(random.uniform(0.0, 10.0), 1)  # Random rainfall between 0-10mm
