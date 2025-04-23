from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class Blind(Device):
    """
    百叶窗设备类，支持百分比开合度控制。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.level = 0  # 0-100 percentage
        DeviceManager.register_device(self)

    def turn_on(self):
        """打开百叶窗（设置为100%）"""
        self.level = 100

    def turn_off(self):
        """关闭百叶窗（设置为0%）"""
        self.level = 0

    def get_status(self) -> str:
        """返回当前开合度"""
        return f"{self.level}% open"

    def set_level(self, level: int):
        """设置百叶窗开合百分比"""
        if 0 <= level <= 100:
            self.level = level
        else:
            raise ValueError("Level must be between 0 and 100")
