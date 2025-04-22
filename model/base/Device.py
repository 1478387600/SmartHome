from abc import ABC, abstractmethod

class Device(ABC):
    """
    所有智能家居设备的抽象基类，定义统一接口。
    """

    def __init__(self, name: str):
        self.name = name

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

    def set_level(self, level: int):
        """
        设置设备等级（用于调光、开合度等）
        如不支持此功能应在子类中抛出 NotImplementedError
        """
        raise NotImplementedError("该设备不支持级别设定")
