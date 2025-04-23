"""
智能家居传感器管理核心模块

该模块实现智能家居系统的传感器管理中心，采用单例模式确保全局传感器状态一致性。
负责传感器的统一注册、状态维护和访问控制，为上层服务提供传感器管理基础能力。

模块功能：
- register_sensor: 注册新传感器到管理系统
- get_sensor_status: 获取指定传感器当前状态
- 单例控制: 保证全局唯一传感器管理实例

项目位置：
- 模块路径: model/Manager/SensorManager.py

依赖模块：
- model.Sensor: 传感器基类接口定义
"""

from typing import Dict
from ..base.Sensor import Sensor


class SensorManager:
    """
    传感器管理单例类，提供传感器注册、状态查询等核心功能。

    特性：
    - 单例模式：通过重写 __new__ 方法保证全局唯一实例
    - 传感器注册表：维护传感器名称到传感器对象的映射关系
    - 状态管理：提供统一的传感器状态查询接口

    典型用法：
    >>> manager = SensorManager()
    >>> manager.register_sensor(TemperatureSensor("living_room_temp"))
    >>> print(manager.get_sensor_status("living_room_temp"))
    """

    _instance = None  # 单例实例存储
    _sensors: Dict[str, Sensor] = {}  # 传感器注册表（传感器名称 -> 传感器对象）

    def __new__(cls):
        """
        单例构造方法，确保只创建一个实例

        返回：
            SensorManager: 全局唯一的传感器管理器实例
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_sensor(cls, sensor: Sensor) -> None:
        """
        注册传感器到管理系统中

        参数：
            sensor (Sensor): 要注册的传感器对象，需实现Sensor接口

        异常：
            ValueError: 当传感器名称已存在时抛出
        """
        if sensor.name in cls._sensors:
            raise ValueError(f"Sensor {sensor.name} already registered")
        cls._sensors[sensor.name] = sensor

    @classmethod
    def get_sensor_status(cls, sensor_id: str) -> str:
        """
        获取指定传感器的当前状态

        参数：
            sensor_id (str): 传感器唯一标识符

        返回：
            str: 传感器状态信息字符串

        异常：
            ValueError: 当传感器未注册时抛出
        """
        sensor = cls._sensors.get(sensor_id)
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} not found")
        return sensor.get_status()
