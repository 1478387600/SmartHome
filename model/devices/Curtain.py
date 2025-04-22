from model.base.Device import Device

class Curtain(Device):
    """
    窗帘设备类，支持基本开关控制。
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.is_open = False

    def turn_on(self):
        """打开窗帘"""
        self.is_open = True

    def turn_off(self):
        """关闭窗帘"""
        self.is_open = False

    def get_status(self) -> str:
        """返回当前状态"""
        return "open" if self.is_open else "closed"
