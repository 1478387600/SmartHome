import sys
from pathlib import Path

# 将项目根目录添加到Python路径（注意：推荐使用包管理方式替代路径修改）
sys.path.append(str(Path(__file__).parent.parent))

from model.devices.AirConditioner import AirConditioner
from model.devices.AirPurifier import AirPurifier
from model.devices.Blind import Blind
from model.devices.Curtain import Curtain
from model.devices.Light import Light
from model.devices.TV import TV
from model.devices.Window import Window
from model.sensors.IndoorTempSensor import IndoorTempSensor
from model.sensors.OutdoorTempSensor import OutdoorTempSensor
from model.sensors.PowerMeter import PowerMeter
from model.sensors.RainSensor import RainSensor
from model.Manager.DeviceManager import DeviceManager
from model.Manager.SensorManager import SensorManager


# def start_simulator():
#     print("启动模拟器...")
#     living_room_ac = AirConditioner("living_room_ac")
#     DeviceManager.register_device(living_room_ac)
#     print(f"DeviceManager注册设备列表：{DeviceManager._devices.keys()}")
#     living_room_ac.set_temperature(24)
#     print(f'living_room_ac temperature: {living_room_ac.get_status()}')


def instantiate_home_devices():
    # 实例化空调（多个房间）
    living_room_ac = AirConditioner("living_room_ac")
    bedroom_ac = AirConditioner("bedroom_ac")

    # 实例化空气净化器
    purifier = AirPurifier("main_purifier")

    # 实例化窗帘和百叶窗
    living_room_curtain = Curtain("living_room_curtain")
    kitchen_blind = Blind("kitchen_blind")

    # 实例化灯（多个区域）
    kitchen_light = Light("kitchen_light")
    bedroom_light = Light("bedroom_light")
    hallway_light = Light("hallway_light")

    # 实例化电视
    tv = TV("living_room_tv")

    # 实例化窗户（多个）
    bathroom_window = Window("bathroom_window")
    bedroom_window = Window("bedroom_window")

    # 实例化传感器
    indoor_temp_sensor = IndoorTempSensor("indoor_temp_sensor")
    outdoor_temp_sensor = OutdoorTempSensor("outdoor_temp_sensor")
    power_meter = PowerMeter("main_power_meter")
    rain_sensor = RainSensor("rain_sensor")

    all_devices = {
        "air_conditioners": [living_room_ac, bedroom_ac],
        "air_purifier": purifier,
        "curtains": [living_room_curtain],
        "blinds": [kitchen_blind],
        "lights": [kitchen_light, bedroom_light, hallway_light],
        "tv": tv,
        "windows": [bathroom_window, bedroom_window],
        "sensors": {
            "indoor_temp": indoor_temp_sensor,
            "outdoor_temp": outdoor_temp_sensor,
            "power_meter": power_meter,
            "rain_sensor": rain_sensor
        }
    }

    register_table = {
        "Devices":DeviceManager._devices.keys(),
        "Sensors":SensorManager._sensors.keys()
    }

    return [all_devices, register_table]


class Simulator:
    def __init__(self):
        print("模拟器启动成功！")
        instantiate_home_devices()


def main():
    simulator = Simulator()
    # instantiate_home_devices()

if __name__ == "__main__":
    main()
