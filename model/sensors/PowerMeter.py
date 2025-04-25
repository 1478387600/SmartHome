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

    def get_status(self) -> int:
        """获取当前耗电量(实现基类抽象方法)"""
        return random.randint(100, 5000)  # 100-5000W随机功率

    def read_value(self):
        """兼容旧接口"""
        return self.get_status()
