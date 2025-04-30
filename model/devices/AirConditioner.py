from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class AirConditioner(Device):
    """
    空调设备类，支持开关控制和温度设置。
    """

    def __init__(self, name: str, width=50, height=50, is_on=False, temperature=26, **kwargs):
        super().__init__(name, width, height, **kwargs)
        self.is_on = is_on
        self.temperature = temperature  # Default temperature in °C
        DeviceManager.register_device(self)

    def to_dict(self):
        data = super().to_dict()  # 调用基类的 to_dict
        data["is_on"] = self.is_on
        data["temperature"] = self.temperature  # 添加设备的特有属性
        return data

    @classmethod
    def from_dict(cls, data):
        instance = super().from_dict(data)  # 调用基类的 from_dict
        instance.is_on = data["is_on"]
        instance.temperature = data["temperature"]  # 重建特有属性
        return instance

    def turn_on(self):
        """打开空调"""
        self.is_on = True

    def turn_off(self):
        """关闭空调"""
        self.is_on = False

    def get_status(self) -> str:
        """返回当前状态和温度"""
        status = "on" if self.is_on else "off"
        return f"{status} at {self.temperature}°C"

    def set_level(self, temp: float):
        """设置空调温度"""
        if 16.0 <= temp <= 30.0:
            self.temperature = temp
        else:
            raise ValueError("Temperature must be between 16°C and 30°C")
