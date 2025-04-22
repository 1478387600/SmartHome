"""
服务器状态管理模块。

该模块负责维护设备运行状态缓存，可用于支持中间状态同步、调试或 Web UI 展示。
"""

from typing import Dict

# 内部状态缓存
device_state_cache: Dict[str, str] = {}

def update_state(device_id: str, state: str):
    """
    更新设备状态。

    参数:
        device_id: 设备名称
        state: 新状态字符串
    """
    device_state_cache[device_id] = state

def get_state(device_id: str) -> str:
    """
    获取设备当前状态。

    参数:
        device_id: 设备名称

    返回:
        状态字符串
    """
    return device_state_cache.get(device_id, "unknown")

def dump_all_states() -> Dict[str, str]:
    """
    返回所有设备当前状态。

    返回:
        设备名到状态的字典
    """
    return device_state_cache.copy()
