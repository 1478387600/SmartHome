from model.base.Sensor import Sensor
from model.Manager.SensorManager import SensorManager
import random

class OutdoorTempSensor(Sensor):
    """
    室外温度传感器类。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.unit = "°C"
        SensorManager.register_sensor(self)

    def read_value(self):
        """读取当前室外温度"""
        return round(random.uniform(-10.0, 40.0), 1)  # Random temp between -10-40°C
