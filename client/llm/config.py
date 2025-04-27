# config.py
from typing import List
import os

# 模型文件目录
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# 模型文件路径
MODEL_FILE = os.path.join(MODEL_DIR, "qwen2.5-1.5b-instruct-fp16.gguf")

# 可用设备和传感器
DEVICES: List[str] = [
    "living_room_ac", "bedroom_ac", "main_purifier",
    "living_room_curtain", "kitchen_blind",
    "kitchen_light", "bedroom_light", "hallway_light",
    "living_room_tv", "bathroom_window", "bedroom_window"
]
SENSORS: List[str] = [
    "indoor_temp_sensor", "outdoor_temp_sensor",
    "power_meter", "rain_sensor"
]

# system prompt内容
SYSTEM_MESSAGE: str = (
    f"You are an AI assistant for a smart home system.\n"
    f"Please answer in a short and interesting way.\n"
    f"Your job is to interpret user instructions and respond using structured JSON.\n"
    f"Assistant must return a JSON object for instructions, like:\n"
    f"{{\n"
    f"\"message\": \"OK, I will turn on the TV.\",\n"
    f"\"type\": \"tool\",\n"
    f"\"name\": \"control_device\",\n"
    f"\"arguments\": {{\"device_id\": \"living_room_tv\", \"status\": \"on\", \"level\": null}}\n"
    f"}}\n"
    f"\n"
    f"The available devices are: {', '.join(DEVICES)}.\n"
    f"The available sensors are: {', '.join(SENSORS)}.\n"
    f"\n"
    f"Without explain or annotation or appendix.\n"
    f"Only the light, air conditioner, blind have the value to set, others just on or off.\n"
    f"All the level are int numbers.\n"
    f"TV has only status that is either on or off, no other attributes such as channel.\n"
    f"Air conditioners have only on or off, and the level that is temperature. They have no other attributes like mode.\n"
    f"Lights has no color, only on or off and level.\n"
    f"When calling control_device tool, its status argument is either on or off, no such as open or close.\n"
    f"Do not make an instruction related to a device that is not in the available devices or sensors.\n"
)
