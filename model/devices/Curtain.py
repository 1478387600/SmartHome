from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class Curtain(Device):
    """
    窗帘设备类，支持基本开关控制。
    """

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.is_open = False
        DeviceManager.register_device(self)

    def to_dict(self):
        data = super().to_dict()  # 调用基类的 to_dict
        data["is_open"] = self.is_open  # 添加设备的特有属性
        return data

    @classmethod
    def from_dict(cls, data):
        instance = super().from_dict(data)  # 调用基类的 from_dict
        instance.is_open = data["is_open"]  # 重建特有属性
        return instance

    def turn_on(self):
        """打开窗帘"""
        self.is_open = True

    def turn_off(self):
        """关闭窗帘"""
        self.is_open = False

    def get_status(self) -> str:
        """返回当前状态"""
        return "open" if self.is_open else "closed"
