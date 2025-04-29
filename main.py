import sys
from pathlib import Path
from tkinter import Tk
from environment.main import Home  # 这里假设你将原来的代码放在了home.py文件里

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

def main():
    # 创建主窗口
    mainWindow = Tk()
    
    # 初始化Home类并启动GUI
    my_system = Home(mainWindow)
    
    # 启动Tkinter主循环
    mainWindow.mainloop()

if __name__ == "__main__":
    main()