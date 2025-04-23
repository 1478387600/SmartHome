from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class AirConditioner(Device):
    """
    空调设备类，支持开关控制和温度设置。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.is_on = False
        self.temperature = 26.0  # Default temperature in °C
        DeviceManager.register_device(self)

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

    def set_temperature(self, temp: float):
        """设置空调温度"""
        if 16.0 <= temp <= 30.0:
            self.temperature = temp
        else:
            raise ValueError("Temperature must be between 16°C and 30°C")
