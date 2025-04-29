from model.base.Device import Device
from model.Manager.DeviceManager import DeviceManager

class Window(Device):
    """
    窗户设备类，支持开关控制。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.is_open = False
        # DeviceManager.register_device(self)

    def turn_on(self):
        """打开窗户"""
        self.is_open = True

    def turn_off(self):
        """关闭窗户"""
        self.is_open = False

    def get_status(self) -> str:
        """返回当前状态"""
        return "open" if self.is_open else "closed"
