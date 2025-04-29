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
        # SensorManager.register_sensor(self)

    def get_status(self) -> float:
        """获取当前降雨量(实现基类抽象方法)"""
        return round(random.uniform(0.0, 10.0), 1)  # 0-10mm随机降雨量

    def read_value(self):
        """兼容旧接口"""
        return self.get_status()
