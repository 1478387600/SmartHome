import sys
from pathlib import Path
from tkinter import *
from tkinter import messagebox
import tkinter as tk
import subprocess
import threading
import asyncio
from environment.simulator import main

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))
from server.runner import main as server


#Creating Setting in Page
class Home:

    def __init__(self, root):
        self.root = root
        self.root.title('Vacuum Cleaner 2D Simulation')

        self.frame1 = tk.LabelFrame(self.root, padx=30, pady=20)
        self.frame1.grid(row=1, padx=30, pady=30)

        self.setting_page = tk.Label(self.root, text='Welcome to Vacuum Cleaner 2D Simulation', font=('Algerian', 22)).grid(row=0, padx=30, pady=20)

        self.numOfRobots = tk.Label(self.frame1, text='*Number of Robots : ', font=('Arial', 14))
        self.numOfRobots.grid(row=1, column=0, pady=10)
        self.numOfBots_entry = tk.Entry(self.frame1, width=10, font=('Arial', 12))
        self.numOfBots_entry.grid(row=1, column=2, pady=10, padx=20)
        self.numOfBots_entry.insert(0, "1")
        self.numOfRobots_label = tk.Label(self.frame1, text='*Minimum 1 Robots, Maximum 10 Robots', font=('Arial', 10))
        self.numOfRobots_label.grid(row=1, column=3, pady=10)

        self.numOfCats = tk.Label(self.frame1, text='*Number of Cats : ', font=('Arial', 14))
        self.numOfCats.grid(row=2, column=0, pady=10)
        self.numOfCats_entry = tk.Entry(self.frame1, width=10, font=('Arial', 12))
        self.numOfCats_entry.grid(row=2, column=2, pady=10, padx=20)
        self.numOfCats_entry.insert(0, "1")
        self.numOfCats_label = tk.Label(self.frame1, text='*Minimum 0 cat, Maximum 5 Cats', font=('Arial', 10))
        self.numOfCats_label.grid(row=2, column=3, pady=10)

        self.amountOfDirt = tk.Label(self.frame1, text='*Amount of Dirt : ', font=('Arial', 14))
        self.amountOfDirt.grid(row=3, column=0, pady=10)
        self.amountOfDirt_entry = tk.Entry(self.frame1, width=10, font=('Arial', 12))
        self.amountOfDirt_entry.grid(row=3, column=2, pady=10, padx=20)
        self.amountOfDirt_entry.insert(0, "1")
        self.amountOfDirt_label = tk.Label(self.frame1, text='*Minimum 0 unit, Maximum 3,000 units', font=('Arial', 10))
        self.amountOfDirt_label.grid(row=3, column=3, pady=10)

        self.timeOfDirt = tk.Label(self.frame1, text='*Generate Dirt Time : ', font=('Arial', 14))
        self.timeOfDirt.grid(row=4, column=0, pady=10)
        self.timeOfDirt_entry = tk.Entry(self.frame1, width=10, font=('Arial', 12))
        self.timeOfDirt_entry.grid(row=4, column=2, pady=10, padx=20)
        self.timeOfDirt_entry.insert(0, "3000")
        self.timeOfDirt_label = tk.Label(self.frame1, text='*Minimum 1,000 time steps, Maximum 20,000 time steps', font=('Arial', 10))
        self.timeOfDirt_label.grid(row=4, column=3, pady=10)
        
        # Checkbox for drawing camera line
        self.drawCameraLine = tk.BooleanVar(value=False)
        self.drawCameraLine_check = tk.Checkbutton(self.frame1, text="Draw Camera Line", variable=self.drawCameraLine, font=('Arial', 12))
        self.drawCameraLine_check.grid(row=5, column=0, columnspan=4, pady=10)

        # Checkbox for drawing grid
        self.drawGridVar = tk.BooleanVar(value=False)
        self.drawGrid_check = tk.Checkbutton(self.frame1, text="Draw Grid", variable=self.drawGridVar, font=('Arial', 12))
        self.drawGrid_check.grid(row=6, column=0, columnspan=4, pady=10)

        # Checkbox for home appliance simulation
        self.applianceSimVar = tk.BooleanVar()
        self.applianceSim_check = tk.Checkbutton(self.frame1, text="Home Appliance Simulation", variable=self.applianceSimVar, font=('Arial', 12))
        self.applianceSim_check.grid(row=7, column=0, columnspan=4, pady=10)

        # Run Button
        self.run_bar = tk.Button(self.frame1, text='Run', padx=10, pady=10, font=('Arial', 12, "bold"),
                                 command=self.open_sim)
        self.run_bar.grid(row=8, column=0, columnspan=4, padx=10, pady=10)

    # To check the condition and open the simulation 
    def open_sim(self):
        try:
            numOfRobots = int(self.numOfBots_entry.get().strip())
            numOfCats = int(self.numOfCats_entry.get().strip())
            amountOfDirt = int(self.amountOfDirt_entry.get().strip())
            timeOfDirt = int(self.timeOfDirt_entry.get().strip())

            #print(f"Robots={numOfRobots}, Cats={numOfCats}, Dirt={amountOfDirt}, Grid={self.drawGridVar.get()}")

            # Check valid number
            if not (1 <= numOfRobots <= 10):
                raise ValueError("Number of robots must be between 1 and 10.")
            if not (0 <= numOfCats <= 5):
                raise ValueError("Number of cats must be between 0 and 5.")
            if not (0 <= amountOfDirt <= 3000):
                raise ValueError("Amount of dirt must be between 0 and 3000.")
            if not (1000 <= timeOfDirt <= 20000):
                raise ValueError("Time of dirt generation must be between 1000 and 20000.")

            drawCamLine = self.drawCameraLine.get()
            drawGrid = self.drawGridVar.get()
            if self.applianceSimVar.get():
                from environment.home_simulator import simulate
                args = [numOfRobots, numOfCats, amountOfDirt, timeOfDirt, drawCamLine, drawGrid]
                simulate(args)
            else:
                main(numOfRobots, numOfCats, amountOfDirt, timeOfDirt, drawCamLine, drawGrid)

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Input Error", f"Unexpected error: {str(e)}")

# mainWindow = tk.Tk()
# my_system = Home(mainWindow)
# mainWindow.mainloop()
