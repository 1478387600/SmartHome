from model.base.Sensor import Sensor
from model.Manager.SensorManager import SensorManager
import random

class IndoorTempSensor(Sensor):
    """
    室内温度传感器类。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.unit = "°C"
        SensorManager.register_sensor(self)

    def read_value(self):
        """读取当前室内温度"""
        return round(random.uniform(18.0, 30.0), 1)  # Random temp between 18-30°C
