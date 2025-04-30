from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class AirPurifier(Device):
    """
    空气净化器设备类，仅支持开关控制。
    """

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.is_on = False
        DeviceManager.register_device(self)

    def to_dict(self):
        data = super().to_dict()  # 调用基类的 to_dict
        data["is_on"] = self.is_on
        return data

    @classmethod
    def from_dict(cls, data):
        instance = super().from_dict(data)  # 调用基类的 from_dict
        instance.is_on = data["is_on"]
        return instance

    def turn_on(self):
        """打开空气净化器"""
        self.is_on = True

    def turn_off(self):
        """关闭空气净化器"""
        self.is_on = False

    def get_status(self) -> str:
        """返回当前状态"""
        return "on" if self.is_on else "off"
