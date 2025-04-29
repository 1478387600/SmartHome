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
        # SensorManager.register_sensor(self)

    def get_status(self) -> float:
        """获取当前室内温度(实现基类抽象方法)"""
        return round(random.uniform(18.0, 30.0), 1)  # 18-30°C随机温度

    def read_value(self):
        """兼容旧接口"""
        return self.get_status()
