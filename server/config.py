"""
服务配置模块。

包含路径常量、环境变量读取、设备初始加载逻辑等，用于支撑 server 启动与运行。
"""

import os
from model.registry import register_device, register_sensor
from model.devices.Light import Light
from model.devices.TV import TV
from model.devices.AirConditioner import AirConditioner
from model.devices.AirPurifier import AirPurifier
from model.devices.Window import Window
from model.devices.Curtain import Curtain
from model.devices.Blind import Blind
from model.sensors.IndoorTempSensor import IndoorTempSensor
from model.sensors.OutdoorTempSensor import OutdoorTempSensor
from model.sensors.RainSensor import RainSensor
from model.sensors.PowerMeter import PowerMeter

def load_devices_and_sensors():
    """
    加载并注册设备与传感器。
    可从配置文件读取或直接硬编码示例。
    """
    # 注册示例设备
    register_device(Light("living_room_light"))
    register_device(TV("living_room_tv"))
    register_device(AirConditioner("bedroom_ac"))
    register_device(AirPurifier("living_room_air_purifier"))
    register_device(Window("kitchen_window"))
    register_device(Curtain("bedroom_curtain"))
    register_device(Blind("living_room_blind"))

    # 注册示例传感器
    register_sensor(IndoorTempSensor("indoor_temp"))
    register_sensor(OutdoorTempSensor("outdoor_temp"))
    register_sensor(RainSensor("rain_sensor"))
    register_sensor(PowerMeter("power_meter"))

def get_env_variable(key: str, default: str = "") -> str:
    """
    从环境变量中读取配置项。

    参数:
        key: 变量名
        default: 默认值

    返回:
        字符串配置值
    """
    return os.getenv(key, default)
