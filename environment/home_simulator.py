
import os
import sys
import json
from pathlib import Path
from threading import Timer
from datetime import datetime
import subprocess
import asyncio

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Now import using absolute paths
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
from model.base.Device import Device
from model.base.Sensor import Sensor
from model.Manager.DeviceManager import DeviceManager
from model.Manager.SensorManager import SensorManager


class HomeSimulator:
    def __init__(self, update_interval=10.0):
        self.update_interval = update_interval  # seconds
        self.timer = None
        self.resource_dir = Path(__file__).parent.parent / "server" / "resources"
        self.resource_dir.mkdir(parents=True, exist_ok=True)

        print("[Simulator] 初始化 HomeSimulator")
        # appliances = self.instantiate_devices()
        self.generate_resources()

    def instantiate_devices(self):
        """实例化所有设备和传感器，并注册"""
        # 设备
        self.devices = [
            AirConditioner("living_room_ac"),
            AirConditioner("bedroom_ac"),
            AirPurifier("main_purifier"),
            Curtain("living_room_curtain"),
            Blind("kitchen_blind"),
            Light("kitchen_light"),
            Light("bedroom_light"),
            Light("hallway_light"),
            TV("living_room_tv"),
            Window("bathroom_window"),
            Window("bedroom_window")
        ]

        # 传感器
        self.sensors = [
            IndoorTempSensor("indoor_temp_sensor"),
            OutdoorTempSensor("outdoor_temp_sensor"),
            PowerMeter("main_power_meter"),
            RainSensor("rain_sensor")
        ]

        print(f"[Simulator] 注册了 {len(self.devices)} 个设备和 {len(self.sensors)} 个传感器")

        return [self.devices, self.sensors]

    def generate_resources(self):
        """生成初始 devices.json 和 sensors.json 文件"""
        devices_data = {
            "devices": [
                {"id": d.name, "type": d.__class__.__name__, "status": d.get_status()} for d in DeviceManager._devices.values()
            ]
        }

        sensors_data = {
            "sensors": [
                {"id": s.name, "type": s.__class__.__name__, "status": s.read_value()} for s in SensorManager._sensors.values()
            ]
        }

        with open(self.resource_dir / "devices.json", "w") as f:
            json.dump(devices_data, f, indent=2)

        with open(self.resource_dir / "sensors.json", "w") as f:
            json.dump(sensors_data, f, indent=2)

        print("[Simulator] 成功生成 resources 文件")

    def update_sensor_status(self):
        """定时更新 sensors.json 文件"""
        sensor_file = self.resource_dir / "sensors.json"
        temp_file = sensor_file.with_suffix(".tmp")

        try:
            sensor_data = {
                "timestamp": datetime.now().isoformat(),
                "sensors": [
                    {"id": s.name, "status": s.get_status(), "type": s.__class__.__name__}
                    for s in Sensor._sensors.values()
                ]
            }

            with open(temp_file, "w") as f:
                json.dump(sensor_data, f, indent=2)

            temp_file.replace(sensor_file)
            # print(f"[{datetime.now():%H:%M:%S}] 成功更新 {len(sensor_data['sensors'])} 个传感器状态")

        except Exception as e:
            # print(f"[{datetime.now():%H:%M:%S}] 更新失败: {e}")
            pass

        finally:
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)

        # 继续下一轮
        self.timer = Timer(self.update_interval, self.update_devices_status)
        self.timer.start()

    def update_devices_status(self):
        """定时更新 devices.json 文件"""
        devices_file = self.resource_dir / "devices.json"
        temp_file = devices_file.with_suffix(".tmp")
        
        try:
            devices_data = {
                "devices": [
                    {"id": d.name, "type": d.__class__.__name__, "status": d.get_status()}
                    for d in DeviceManager._devices.values()
                ]
            }
            
            # Write updated devices data to temporary file
            with open(temp_file, "w") as f:
                json.dump(devices_data, f, indent=2)
            
            # Replace the original devices file with the updated temporary file
            temp_file.replace(devices_file)
            # print(f"[{datetime.now():%H:%M:%S}] 成功更新 {len(devices_data['devices'])} 个设备状态")
        
        except Exception as e:
            # print(f"[{datetime.now():%H:%M:%S}] 更新失败: {e}")
            pass
        
        finally:
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
        
        # Continue next round of updating
        self.timer = Timer(self.update_interval, self.update_devices_status)  # Corrected this line
        self.timer.start()

    def start_sensors(self):
        """启动模拟器"""
        print("[Simulator] 启动传感器状态更新")
        self.update_sensor_status()
    
    def start_devices(self):
        """启动模拟器"""
        print("[Simulator] 启动传感器状态更新")
        self.update_devices_status()

    def stop(self):
        """停止模拟器"""
        if self.timer:
            self.timer.cancel()
            print("[Simulator] 停止传感器状态更新")

def simulate(args):
    simulator = HomeSimulator()
    simulator.start_sensors()
    simulator.start_devices()
    appliances = simulator.instantiate_devices()
    numOfRobots, numOfCats, amountOfDirt, timeOfDirt, drawCamLine, drawGrid = args
    from environment.simulator_with_appliance import sim_main
    sim_main(numOfRobots, numOfCats, amountOfDirt, timeOfDirt, drawCamLine, drawGrid, appliances)
    subprocess.Popen(
        ["uv", "run", "server/app.py"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # simulator.stop()


# if __name__ == "__main__":
#     raw_args = sys.argv[1]
#     parts = list(map(int, raw_args.split(",")))

#     if len(parts) != 6:
#         raise ValueError(f"收到的参数数量不对：{parts}")

#     args = parts[:4] + list(map(bool, parts[4:]))  # 把前四个 int，后两个 bool
    
#     main(args)
