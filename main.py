import sys
from pathlib import Path
import multiprocessing
from subprocess import Popen

# 将项目根目录添加到Python路径，确保可以导入项目中的模块
sys.path.append(str(Path(__file__).parent.parent))

# 导入MCP服务器相关模块
from mcp.server import FastMCP
from mcp.server.models import InitializationOptions

def run_simulator():
    """
    启动模拟器的函数
    该函数负责导入并运行模拟器模块（simulator.py）
    确保模拟器的main函数能够正常运行
    """
    print("启动模拟器...")
    try:
        import simulator
        simulator.main()  # 调用模拟器中的main函数
        print("模拟器启动成功！")
    except Exception as e:
        print(f"模拟器启动失败: {e}")

def run_server():
    """
    启动服务器的函数
    该函数负责创建并启动MCP服务端，处理设备控制的工具
    """
    print("启动MCP服务器...")
    mcp = FastMCP('smart-home')

    # 定义一个工具来控制设备开关
    @mcp.tool()
    def switch_device(device_id: str, status: str) -> str:
        """
        设备开关控制函数
        根据传入的设备ID和状态（开/关）来控制设备
        """
        print(f"正在控制设备 {device_id}，目标状态: {status}")
        # 假设有个get_device_by_id函数来获取设备实例
        device = get_device_by_id(device_id)
        if status == "on":
            device.turn_on()  # 开启设备
            print(f"设备 {device_id} 已开启")
        else:
            device.turn_off()  # 关闭设备
            print(f"设备 {device_id} 已关闭")
        return f"设备 {device_id} 状态已设置为 {status}"

    # 启动MCP服务器并监听标准输入输出
    mcp.run(transport='stdio')
    print("MCP服务器已启动，等待请求...")

if __name__ == "__main__":
    """
    主程序入口，启动模拟器和服务器并行运行
    使用multiprocessing模块启动两个独立进程：一个用于运行模拟器，另一个用于运行MCP服务器
    """
    print("主程序启动中...")

    # 启动模拟器的进程
    process_simulator = multiprocessing.Process(target=run_simulator)
    # 启动服务器的进程
    process_server = multiprocessing.Process(target=run_server)

    # 启动两个进程
    process_simulator.start()
    process_server.start()

    # 等待两个进程结束
    process_simulator.join()
    process_server.join()

    print("主程序结束")
