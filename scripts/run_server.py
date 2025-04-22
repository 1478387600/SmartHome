"""
启动 MCP Server。
"""

import os
import sys

# 确保可以导入 server 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.main import mcp

if __name__ == "__main__":
    # print("Starting MCP SmartHome Server...")
    # try:
    #     mcp.run(transport="stdio")
    # except Exception as e:
    #     print(f"[Server crashed] {type(e).__name__}: {e}")
    try:
        print("Starting MCP SmartHome Server...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nServer shutdown by user")
    except Exception as e:
        print(f"[Server crashed] {type(e).__name__}: {e}")
    finally:
        print("Server process terminated")
