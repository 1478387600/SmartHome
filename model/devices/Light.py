from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class Light(Device):
    """
    灯光设备类，支持亮度百分比控制。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.brightness = 0  # 0-100 percentage
        DeviceManager.register_device(self)

    def turn_on(self):
        """打开灯（默认设置为50%亮度）"""
        self.brightness = 50 if self.brightness == 0 else self.brightness

    def turn_off(self):
        """关闭灯（亮度设置为0%）"""
        self.brightness = 0

    def get_status(self) -> str:
        """返回当前亮度状态"""
        return f"{self.brightness}% brightness"

    def set_level(self, level: int):
        """设置灯光亮度百分比"""
        if 0 <= level <= 100:
            self.brightness = level
        else:
            raise ValueError("Brightness must be between 0 and 100")
