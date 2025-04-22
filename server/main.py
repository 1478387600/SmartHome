"""
MCP Server 启动入口。

该模块初始化并启动 FastMCP 服务，注册资源与工具，定义服务器元信息与生命周期管理。

初始化并运行FastMCP服务
注册资源和工具
管理设备生命周期
提供标准输入输出接口
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.app import mcp
from server import tools, resources
from server.config import load_devices_and_sensors
import logging

# 配置日志记录
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[
        logging.FileHandler('server/logs/server.log'),
        logging.StreamHandler()
    ]
)

# 初始化设备
load_devices_and_sensors()

if __name__ == "__main__":
    print("📡 Running MCP server...")
    mcp.run(transport="stdio")
    print("✅ MCP server.run() returned")
