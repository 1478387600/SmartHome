"""
智能家居设备管理核心模块

该模块实现智能家居系统的设备管理中心，采用单例模式确保全局设备状态一致性。
负责设备的统一注册、状态维护和访问控制，为上层服务提供设备管理基础能力。

模块功能：
- register_device: 注册新设备到管理系统
- get_device_status: 获取指定设备当前状态
- 单例控制: 保证全局唯一设备管理实例

项目位置：

- 模块路径: model/Manager/DeviceManager.py

依赖模块：
- model.Device: 设备基类接口定义
"""

from typing import Dict
from ..base.Device import Device


class DeviceManager:
    """
    设备管理单例类，提供设备注册、状态查询等核心功能。

    特性：
    - 单例模式：通过重写 __new__ 方法保证全局唯一实例
    - 设备注册表：维护设备名称到设备对象的映射关系
    - 状态管理：提供统一的设备状态查询接口

    典型用法：
    >>> manager = DeviceManager()
    >>> manager.register_device(Light("living_room_light"))
    >>> print(manager.get_device_status("living_room_light"))
    """

    _instance = None  # 单例实例存储
    _devices: Dict[str, Device] = {}  # 设备注册表（设备名称 -> 设备对象）

    def __new__(cls):
        """
        单例构造方法，确保只创建一个实例

        返回：
            DeviceManager: 全局唯一的设备管理器实例
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_device(cls, device: Device) -> None:
        """
        注册设备到管理系统中

        参数：
            device (Device): 要注册的设备对象，需实现Device接口

        异常：
            ValueError: 当设备名称已存在时抛出
        """
        if device.name in cls._devices:
            raise ValueError(f"Device {device.name} already registered")
        cls._devices[device.name] = device

    @classmethod
    def get_device_status(cls, device_id: str) -> str:
        """
        获取指定设备的当前状态

        参数：
            device_id (str): 设备唯一标识符

        返回：
            str: 设备状态信息字符串

        异常：
            ValueError: 当设备未注册时抛出
        """
        device = cls._devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        return device.get_status()
