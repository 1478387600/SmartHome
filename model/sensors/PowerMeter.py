from model.base.Sensor import Sensor
from model.Manager.SensorManager import SensorManager
import random

class PowerMeter(Sensor):
    """
    电表传感器类。
    """

    def __init__(self, name: str, unit="W"):
        super().__init__(name)
        self.unit = unit
        SensorManager.register_sensor(self)

    def to_dict(self):
        data = super().to_dict()  # 调用基类的 to_dict
        data["unit"] = self.unit  # 添加设备的特有属性
        return data

    @classmethod
    def from_dict(cls, data):
        instance = super().from_dict(data)  # 调用基类的 from_dict
        instance.unit = data["unit"]  # 重建特有属性
        return instance

    def get_status(self) -> int:
        """获取当前耗电量(实现基类抽象方法)"""
        return random.randint(100, 5000)  # 100-5000W随机功率

    def read_value(self):
        """兼容旧接口"""
        return self.get_status()
