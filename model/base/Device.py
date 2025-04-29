from abc import ABC, abstractmethod

class Device(ABC):
    """
    所有智能家居设备的抽象基类，定义统一接口。
    """
    _devices = {}  # 类属性维护设备注册表

    def __init__(self, name: str, width=50, height=50):
        self.name = name
        self.width = width
        self.height = height
        self.__class__._devices[name] = self
        self._canvas_items = {}  # 记录canvas上画的元素，方便后续更新

    @abstractmethod
    def turn_on(self):
        """打开设备"""
        pass

    @abstractmethod
    def turn_off(self):
        """关闭设备"""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """获取设备当前状态"""
        pass

    @classmethod
    def get_status(cls, device_id: str) -> str:
        """通过设备ID获取状态"""
        device = cls._devices.get(device_id)
        if device:
            return device.get_status()
        raise ValueError(f"Device {device_id} not found")

    def set_level(self, level: int):
        """
        设置设备等级（用于调光、开合度等）
        如不支持此功能应在子类中抛出 NotImplementedError
        """
        raise NotImplementedError("该设备不支持级别设定")
    
    def draw(self, canvas, x=None, y=None, image=None):
        """在canvas上绘制自己，包括图片和状态文字"""
        if x is not None:
            self.centreX = x
        if y is not None:
            self.centreY = y
        if image is not None:
            self.image = image

        x1 = self.centreX - self.width // 2
        y1 = self.centreY - self.height // 2
        x2 = self.centreX + self.width // 2
        y2 = self.centreY + self.height // 2

        # 如果之前画过，需要先删掉（避免叠图）
        if self._canvas_items:
            for item in self._canvas_items.values():
                canvas.delete(item)
            self._canvas_items.clear()

        # 画图片
        if self.image:
            img_item = canvas.create_image(self.centreX, self.centreY, image=self.image, tags=self.name)
        else:
            img_item = canvas.create_rectangle(x1, y1, x2, y2, fill="gray", tags=self.name)

        # 画状态文字
        status_text = self.get_status()  # 让子类/主类提供状态字符串
        text_item = canvas.create_text(self.centreX + self.width, 
                                       self.centreY, 
                                       text=status_text, 
                                       tags="appliance_status",
                                       anchor="w", 
                                       font=("Arial", 10))
        # 记录item
        self._canvas_items['image'] = img_item
        self._canvas_items['text'] = text_item
