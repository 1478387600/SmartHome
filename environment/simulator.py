from PIL import Image, ImageTk
import tkinter as tk
import random
import math
import numpy as np
import time
import sys
from .astar_path import a_star
import os
import pygame
pygame.mixer.init()

image_cache = {}  # Global dictionary to store images

class Brain():
    def __init__(self, botp):
        self.bot = botp
        self.turningCount = 0
        self.movingCount = random.randrange(50, 100)
        self.currentlyTurning = False
        self.time = 0
        self.trainingSet = []
        self.dangerThreshold = 0
        self.goalReached = None
        self.path_a = []

    def thinkAndAct(self, lightL, lightR, chargerL, chargerR, x, y, sl, sr, battery, camera, collision):
        dangerDetected = False
  
        # Danger learning phase
        trainingTime = 1000
        if self.time < trainingTime:
            self.trainingSet.append((camera, collision))
        elif self.time == trainingTime:
            warningValues = []
            for i, tt in enumerate(self.trainingSet):
                if i >= 5 and tt[1] == True:
                    warningValues.append(self.trainingSet[i - 5][0])
            countWV = 0
            sumWV = 0
            for wv in warningValues:
                if not wv == [0] * 9:
                    sumWV += max(wv)
                    countWV += 1
            if countWV != 0:
                self.dangerThreshold = sumWV / countWV
                print("Vision training complete. Danger threshold:", self.dangerThreshold)
        elif self.time > trainingTime:
            if any(c > self.dangerThreshold for c in camera):
                dangerDetected = True

        self.time += 1

        speedLeft = 0.0
        speedRight = 0.0
        newX = None
        newY = None


        current_cell = (int(x // 60), int(y // 60))     # Create by NattapongNEADTIP_20717335

        # Create by NattapongNEADTIP_20717335
        # If the robot is in the goal position
        if self.goalReached == current_cell:
            #print(f"Fully reached goal: {self.goalReached}")
            self.path_a = []
            self.goalReached = None
            return 0.0, 0.0, None, None, dangerDetected, True
        
        # Create by NattapongNEADTIP_20717335
        # When the robot have a low battery or full collected dirt.
        if (self.bot.battery < 3000 or self.bot.collectedDirt > 150) and not self.path_a:
            grid = self.bot.map()
            start = (int(self.bot.x // 60), int(self.bot.y // 60))
            goals = [(1, 5), (3, 10), (5, 2), (12, 10), (15, 2), (18, 6)]
            
            self.path_a, self.goalReached = a_star(grid, start, goals)

        # Follow A* path
        # Create by NattapongNEADTIP_20717335
        if self.path_a and (self.bot.battery < 3000 or self.bot.collectedDirt > 150):
        
            targetGrid = self.path_a[0]
            target = [targetGrid[0] * 60 + 30, targetGrid[1] * 60 + 30]

            dx = target[0] - x
            dy = target[1] - y
            angle_to_target = math.atan2(dy, dx)
            angle_diff = (angle_to_target - self.bot.theta + math.pi) % (2 * math.pi) - math.pi

            angle_threshold = 0.3

            if abs(angle_diff) < angle_threshold:
                speedLeft = 1.0
                speedRight = 1.0
            elif angle_diff > 0:
                speedLeft = 1.0
                speedRight = -1.0
            else:
                speedLeft = -1.0
                speedRight = 1.0

            if math.hypot(dx, dy) < 30:
                #print(f"Reached: {targetGrid}")
                del self.path_a[0]

                if len(self.path_a) == 0:
                    #print("Full path complete, switching to wander mode")
                    self.goalReached = None

        else:
            # Wandering fallback
            if self.currentlyTurning:
                speedLeft = -2.0
                speedRight = 2.0
                self.turningCount -= 1
            else:
                speedLeft = 2.5
                speedRight = 2.5
                self.movingCount -= 1

            if self.movingCount == 0 and not self.currentlyTurning:
                self.turningCount = random.randrange(0, 10)
                self.currentlyTurning = True
            if self.turningCount == 0 and self.currentlyTurning:
                self.movingCount = random.randrange(50, 100)
                self.currentlyTurning = False

        completed = self.path_a and len(self.path_a) == 0   # Create by NattapongNEADTIP_20717335

        if chargerL + chargerR > 1000 and battery < 10000 :
            speedLeft = 0.0
            speedRight = 0.0

        return speedLeft, speedRight, newX, newY, dangerDetected, completed


class Bot():

    def __init__(self,namep,canvasp, passiveObjectsp,counterp):
        self.name = namep
        self.canvas = canvasp
        self.x = random.randint(60,1100)
        self.y = random.randint(150,650)
        self.theta = random.uniform(0.0,2.0*math.pi)
        #self.theta = 0
        self.ll = 60 #axle width
        self.sl = 0.0
        self.sr = 0.0
        self.battery = 10000
        self.collectedDirt = 0
        self.fullDirt = "Full"

        self.passiveObjects = passiveObjectsp
        self.counter = counterp
 

    def thinkAndAct(self, agents, passiveObjects, canvas):
        lightL, lightR = self.senseLight(passiveObjects)
        chargerL, chargerR = self.senseChargers(passiveObjects)
        view = self.look(canvas, agents)
        wallAhead = self.senseWalls(passiveObjects)
        collision = self.collision(agents)

        # Wall avoidance check
        if wallAhead:
            #print(f"{self.name} detected wall – avoiding")
            self.theta = random.uniform(0.0,2.0*math.pi)
            self.sl = 2.0
            self.sr = -2.0
            return

        self.sl, self.sr, xx, yy, dangerDetected, completed = self.brain.thinkAndAct\
            (lightL, lightR, chargerL, chargerR, self.x, self.y, \
             self.sl, self.sr, self.battery, view, collision)
        
        if (dangerDetected):
            self.reactToDanger(agents)

        if xx != None:
            self.x = xx
        if yy != None:
            self.y = yy

        if completed:
            return
        
    def setBrain(self,brainp):
        self.brain = brainp

    # Create by NattapongNEADTIP_20717335
    def map(self):
        if not hasattr(self, 'cached_grid'):
            grid = np.random.randint(1, 5, (20, 12), dtype=np.int16)

            # Static walls
            grid[0, :] = 5
            grid[19, :] = 5
            grid[:, 0] = 5
            grid[:, 1] = 5
            grid[:, 11] = 5
            grid[11, 2:5] = 5
            grid[1:7, 8] = 5

            # Goals
            grid[1, 5] = 1
            grid[3, 10] = 1
            grid[5, 2] = 1
            grid[12, 10] = 1
            grid[15, 2] = 1
            grid[18, 6] = 1
            

            self.cached_grid = grid
        return self.cached_grid


    def senseWalls(self, passiveObjects, buffer=0):
        for pos in self.cameraPositions:
            for obj in passiveObjects:
                if isinstance(obj, Walls):
                    x1, y1, x2, y2 = obj.getBounds()
                    if (x1 - buffer <= pos[0] <= x2 + buffer) and (y1 - buffer <= pos[1] <= y2 + buffer):
                        return True
        return False

    # Create by NattapongNEADTIP_20717335
    def reactToDanger(self, agents):
        print("dangerous situation")
        sound_path = os.path.join(os.path.dirname(__file__), "436589.wav")
        pygame.mixer.Sound(sound_path).play()

        for ag in agents:
            if isinstance(ag,Cat):
                distance = self.distanceTo(ag)
                if distance < 70:  # jump only if the cat is within 60 pixels
                    ag.jump(big=True)


    def look(self, canvas, agents):
        self.view = [0] * 30
        for idx, pos in enumerate(self.cameraPositions):
            for cc in agents:
                if isinstance(cc, Cat):
                    dd = self.distanceTo(cc)
                    scaledDistance = max(400 - dd, 0) / 400
                    ncx = cc.x - pos[0]
                    ncy = cc.y - pos[1]
                    m = math.tan(self.theta)
                    A = m * m + 1
                    B = 2 * (-m * ncy - ncx)
                    r = 70
                    C = ncy * ncy - r * r + ncx * ncx
                    if B * B - 4 * A * C >= 0 and scaledDistance > self.view[idx]:
                        self.view[idx] = scaledDistance

        # Delete previous view bars
        canvas.delete(self.name + "_view")

        radius = 30
        robot_width = radius * 2
        num_bars = 9
        bar_width = robot_width / num_bars
        bar_height = 10
        offset_x = -(robot_width / 2)
        offset_y = 40

        for vv in range(num_bars):
            x0 = self.x + offset_x + vv * bar_width
            y0 = self.y + offset_y
            x1 = x0 + bar_width
            y1 = y0 + bar_height

            if self.view[vv] == 0:
                canvas.create_rectangle(x0, y0, x1, y1, fill="white", tags=self.name + "_view")
            else:
                danger = self.view[vv]
                if danger < 0.5:
                    # Green to Yellow
                    green = 255
                    red = int(2 * danger * 255)
                else:
                    # Yellow to Red
                    green = int((1 - 2 * (danger - 0.5)) * 255)
                    red = 255

                red = max(0, min(255, red))
                green = max(0, min(255, green))
                color = f"#{red:02x}{green:02x}00"

                canvas.create_rectangle(x0, y0, x1, y1, fill=color, tags=self.name + "_view")

        return self.view

    # returns the output from polling the light sensors
    def senseLight(self, passiveObjects):
        lightL = 0.0
        lightR = 0.0
        for pp in passiveObjects:
            if isinstance(pp,Lamp):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt((lx-self.x)**2 + (ly-self.y)**2)
                distanceR = distanceL
                lightL += 200000/(distanceL**2)
                lightR += 200000/(distanceR**2)
        return lightL, lightR

    # returns sensors values that detect chargers
    def senseChargers(self, passiveObjects):
        chargerL = 0.0
        chargerR = 0.0
        for pp in passiveObjects:
            if isinstance(pp,Charger):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt((lx-self.x)**2 + (ly-self.y)**2)
                distanceR = distanceL
                chargerL += 200000/(distanceL**2)
                chargerR += 200000/(distanceR**2)
        return chargerL, chargerR

    def distanceTo(self,obj):
        xx,yy = obj.getLocation()
        return math.sqrt( math.pow(self.x-xx,2) + math.pow(self.y-yy,2))

    def distance(self,otherRobot):
        return math.sqrt( (self.x-otherRobot.x)*(self.x-otherRobot.x) + \
                          (self.y-otherRobot.y)*(self.y-otherRobot.y) )

    # what happens at each timestep
    def update(self,canvas,passiveObjects,dt):
        # for now, the only thing that changes is that the robot moves
        #   (using the current settings of self.sl and self.sr)
        if self.battery > 3000:
            self.battery -= 5

        if self.battery <= 3000:
            self.battery -= 1

        for rr in passiveObjects:
            if isinstance(rr,Charger) and self.distanceTo(rr)<40:
                self.battery += 25
                if self.collectedDirt > 0:
                    self.collectedDirt -= 1
                if self.collectedDirt <= 0:
                    self.collectedDirt = 0

                if self.battery >= 10000:
                    self.battery = 10000

        if self.battery<=0:
            self.battery = 0

        self.move(canvas,dt)

    # draws the robot at its current position
    def draw(self,canvas):

        radius = 30  # Radius of the circular robot body

        # Camera points evenly spaced along front arc (semi-circle)
        self.cameraPositions = []
        num_cameras = 30
        arc_start = -math.pi / 3  # -60 degrees
        arc_end = math.pi / 3     # +60 degrees
        for i in range(num_cameras):
            angle_offset = arc_start + i * (arc_end - arc_start) / (num_cameras - 1)
            angle = self.theta + angle_offset
            cam_x = self.x + radius * math.cos(angle)
            cam_y = self.y + radius * math.sin(angle)
            self.cameraPositions.append((cam_x, cam_y))
            canvas.create_oval(cam_x - 2, cam_y - 2, cam_x + 2, cam_y + 2, fill="purple1", tags=self.name)
            

        # Draw circular robot body
        canvas.create_oval(self.x - radius, self.y - radius, self.x + radius, self.y + radius, fill="blue", tags=self.name)

        # Display battery level
        #canvas.create_text(self.x, self.y, text=str(self.battery), tags=self.name, fill="white", font="bold")
        canvas.create_text(self.x, self.y, text=str(self.battery), tags=self.name, fill="white", font="bold")
        canvas.create_text(self.x, self.y + 18, text=self.collectedDirt, tags=self.name, fill="yellow", font=("Arial", 12))

        if self.collectedDirt >= 150:
            canvas.create_text(self.x, self.y - 15, text="Full", tags=self.name, fill="coral", font=("Arial", 10, "bold"))
        elif self.battery <= 3000:
            canvas.create_text(self.x, self.y - 15, text="Low", tags=self.name, fill="yellow", font=("Arial", 10, "bold"))
        
        # Wheel markers
        wheel_offset_angle = math.pi / 2
        left_wheel_x = self.x + radius * math.cos(self.theta + wheel_offset_angle)
        left_wheel_y = self.y + radius * math.sin(self.theta + wheel_offset_angle)
        right_wheel_x = self.x + radius * math.cos(self.theta - wheel_offset_angle)
        right_wheel_y = self.y + radius * math.sin(self.theta - wheel_offset_angle)
        canvas.create_oval(left_wheel_x-3, left_wheel_y-3, left_wheel_x+3, left_wheel_y+3, fill="red", tags=self.name)
        canvas.create_oval(right_wheel_x-3, right_wheel_y-3, right_wheel_x+3, right_wheel_y+3, fill="yellow", tags=self.name)
    

        # light sensors around the robot
        self.sensorPositions = []
        num_sensors = 8
        sensor_radius = 30

        wheel_angles = [(self.theta + math.pi / 2) % (2 * math.pi),     # left wheel angle
                        (self.theta - math.pi / 2) % (2 * math.pi)]     # right wheel angle

        for i in range(num_sensors):
            angle = (self.theta + i * (2 * math.pi / num_sensors)) % (2 * math.pi)
            sx = self.x + sensor_radius * math.cos(angle)
            sy = self.y + sensor_radius * math.sin(angle)
            self.sensorPositions.append((sx, sy))

            # Skip drawing if near left/right wheel angle
            if any(abs(angle - wa) < 0.3 or abs(angle - wa) > (2 * math.pi - 0.3) for wa in wheel_angles):
                continue

            canvas.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill="cyan", tags=self.name)

    # handles the physics of the movement
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self,canvas,dt):
        if self.battery==0:
            self.sl = 0
            self.sr = 0

        # Compute differential drive
        if self.sl == self.sr:
            # Straight-line movement
            dx = self.sl * math.cos(self.theta)
            dy = self.sl * math.sin(self.theta)
            self.x += dx
            self.y += dy
        else:
            try:
                R = (self.ll / 2.0) * ((self.sl + self.sr) / (self.sl - self.sr))
            except ZeroDivisionError:
                R = 0

            omega = (self.sl - self.sr) / self.ll
            ICCx = self.x - R * math.sin(self.theta)
            ICCy = self.y + R * math.cos(self.theta)

            # Rotation matrix update
            m = np.array([[math.cos(omega * dt), -math.sin(omega * dt), 0],
                          [math.sin(omega * dt),  math.cos(omega * dt), 0],
                          [0, 0, 1]])

            v1 = np.array([[self.x - ICCx], [self.y - ICCy], [self.theta]])
            v2 = np.array([[ICCx], [ICCy], [omega * dt]])
            newv = np.dot(m, v1) + v2

            self.x = newv.item(0)
            self.y = newv.item(1)
            self.theta = newv.item(2) % (2.0 * math.pi)

        canvas.delete(self.name)
        self.draw(canvas)

        self.look(canvas, canvas.agents)


    def collectDirt(self, canvas, passiveObjects, count):
        toDelete = []
        for idx,rr in enumerate(passiveObjects):
            if isinstance(rr,Dirt):
                if self.distanceTo(rr)<30:
                    canvas.delete(rr.name)
                    toDelete.append(idx)
                    count.itemCollected(canvas)
                    self.collectedDirt += 1
        for ii in sorted(toDelete,reverse=True):
            del passiveObjects[ii]
        return passiveObjects

    def collision(self,agents):
        collision = False
        for rr in agents:
            if isinstance(rr,Cat):
                if self.distanceTo(rr)<50.0:
                    sound_path = os.path.join(os.path.dirname(__file__), "385892.wav")
                    pygame.mixer.Sound(sound_path).play()
                    collision = True
                    rr.jump()

        return collision
    
class Cat:
    def __init__(self,namep,canvasp):
        self.x = random.randint(100,900)
        self.y = random.randint(150,600)
        self.theta = random.uniform(0.0,2.0*math.pi)
        self.name = namep
        self.canvas = canvasp
        self.vl = 1.0
        self.vr = 1.0
        self.turning = 0
        self.moving = random.randrange(50,100)
        self.currentlyTurning = False
        self.ll = 20
        imgFile = Image.open("environment\cat.png")
        imgFile = imgFile.resize((30,30), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(imgFile)
        image_cache["cat"] = self.image  # Prevent garbage collection by storing globally
    
        
    def draw(self,canvas):
        body = canvas.create_image(self.x,self.y,image=self.image,tags=self.name)

    def getLocation(self):
        return self.x, self.y

    def thinkAndAct(self, agents, passiveObjects, canvas):

        if self.detectWall(passiveObjects):
            #print(f"{self.name} avoiding wall")
            self.theta = random.uniform(0.0,2.0*math.pi)
            self.vl = 1.0
            self.vr = 1.0
            return
        
        else:
            # wandering behaviour
            if self.currentlyTurning==True:
                self.vl = -2.0
                self.vr = 2.0
                self.turning -= 1
            else:
                self.vl = 1.0
                self.vr = 1.0
                self.moving -= 1
            if self.moving==0 and not self.currentlyTurning:
                self.turning = random.randrange(20,40)
                self.currentlyTurning = True
            if self.turning==0 and self.currentlyTurning:
                self.moving = random.randrange(50,100)
                self.currentlyTurning = False

    def update(self,canvas,passiveObjects,dt):
        self.move(canvas,dt)
            
    def move(self,canvas,dt):
        if self.vl==self.vr:
            R = 0
        else:
            R = (self.ll/2.0)*((self.vr+self.vl)/(self.vl-self.vr))
        omega = (self.vl-self.vr)/self.ll
        ICCx = self.x-R*math.sin(self.theta) #instantaneous centre of curvature
        ICCy = self.y+R*math.cos(self.theta)
        m = np.matrix( [ [math.cos(omega*dt), -math.sin(omega*dt), 0], \
                        [math.sin(omega*dt), math.cos(omega*dt), 0],  \
                        [0,0,1] ] )
        v1 = np.matrix([[self.x-ICCx],[self.y-ICCy],[self.theta]])
        v2 = np.matrix([[ICCx],[ICCy],[omega*dt]])
        newv = np.add(np.dot(m,v1),v2)
        newX = newv.item(0)
        newY = newv.item(1)
        newTheta = newv.item(2)
        newTheta = newTheta%(2.0*math.pi) #make sure angle doesn't go outside [0.0,2*pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta        
        if self.vl==self.vr: # straight line movement
            self.x += self.vr*math.cos(self.theta) #vr wlog
            self.y += self.vr*math.sin(self.theta)

        canvas.delete(self.name)
        self.draw(canvas)

    def jump(self, big=False):

        # Define jump range based on size
        dx = random.randint(50, 100) if big else random.randint(20, 50)
        dy = random.randint(50, 100) if big else random.randint(20, 50)

        # Determine direction based on position near edges
        if self.x < 100:
            self.x += dx
        elif self.x > 900:
            self.x -= dx
        else:
            self.x += random.choice([-1, 1]) * dx

        if self.y < 150:
            self.y += dy
        elif self.y > 650:
            self.y -= dy
        else:
            self.y += random.choice([-1, 1]) * dy

        self.x = max(50, min(1170, self.x))
        self.y = max(120, min(680, self.y))

        #self.updateMap()
        self.canvas.delete(self.name)
        self.draw(self.canvas)
        
    def detectWall(self, passiveObjects):
        # Simple bounding box overlap check
        for obj in passiveObjects:
            if isinstance(obj, Walls):
                x1, y1, x2, y2 = obj.getBounds()
                buffer = 30  # radius around cat
                if (x1 - buffer <= self.x <= x2 + buffer) and (y1 - buffer <= self.y <= y2 + buffer):
                    return True
        return False


class Lamp():
    def __init__(self,namep):
        self.centreX = random.randint(400,600)
        self.centreY = random.randint(360,540)
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="yellow",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY
    

class Charger():
    def __init__(self,namep, xc, yc):
        self.centreX = xc
        self.centreY = yc
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="red",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY
    

class Dirt:
    def __init__(self,namep):
        self.centreX = random.randint(30,1170)
        self.centreY = random.randint(120,690)
        self.name = namep

    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-1,self.centreY-1, \
                                  self.centreX+1,self.centreY+1, \
                                  fill="grey",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY
    
    
class Walls:
    def __init__(self, namep, x=None, y=None, width=None, height=None):
        self.centreX = x
        self.centreY = y
        self.width = width
        self.height = height
        self.name = namep

    def draw(self, canvas):
        self.x1 = self.centreX - self.width // 2
        self.y1 = self.centreY - self.height // 2
        self.x2 = self.centreX + self.width // 2
        self.y2 = self.centreY + self.height // 2
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill="black", tags=self.name)

    def getBounds(self):
        return self.x1, self.y1, self.x2, self.y2


class Counter:
    def __init__(self):
        self.dirtCollected = 0

    def itemCollected(self,canvas):
        self.dirtCollected += 1
        canvas.delete("dirtCount")
        canvas.create_text(50,50,anchor="w",\
                        text="Total Collected Dirt: "+str(self.dirtCollected),\
                        tags="dirtCount", font=("Arial", 20, "bold"), fill="darkgreen")


def initialise(window):
    window.resizable(False,False)
    canvas = tk.Canvas(window,width=1200,height=720)
    canvas.pack()
    return canvas

def buttonClicked(x, y, agents):
    for rr in agents:
        if isinstance(rr, Bot):
            rr.x = x
            rr.y = y
            rr.brain.path_a = []
            rr.brain.goalReached = None

def createObjects(canvas,noOfBots,noOfLights,amountOfDirt,noOfCats):
    agents = []
    passiveObjects = []

    for i in range(0,noOfCats):
        cat = Cat("Cat"+str(i),canvas)
        agents.append(cat)
        cat.draw(canvas)

    for i in range(0,noOfLights):
        lamp = Lamp("Lamp"+str(i))
        passiveObjects.append(lamp)
        lamp.draw(canvas)

    charger = Charger("Charger1",90, 330)
    passiveObjects.append(charger)
    charger.draw(canvas)
    charger = Charger("Charger2",210, 630)
    passiveObjects.append(charger)
    charger.draw(canvas)
    charger = Charger("Charger3", 330, 150)
    passiveObjects.append(charger)
    charger.draw(canvas)
    charger = Charger("Charger4",750, 630)
    passiveObjects.append(charger)
    charger.draw(canvas)
    charger = Charger("Charger5",930, 150)
    passiveObjects.append(charger)
    charger.draw(canvas)
    charger = Charger("Charger6",1110, 390)
    passiveObjects.append(charger)
    charger.draw(canvas)
    
    # hub1 = WiFiHub("Hub1",950,135)
    # passiveObjects.append(hub1)
    # hub1.draw(canvas)
    # hub2 = WiFiHub("Hub2",50,650)
    # passiveObjects.append(hub2)
    # hub2.draw(canvas)

    for i in range(0,amountOfDirt):
        dirt = Dirt("Dirt"+str(i))
        passiveObjects.append(dirt)
        dirt.draw(canvas)


    wall1 = Walls("Wall1", x=600, y=90, width=1200, height=20)
    wall2 = Walls("Wall2", x=600, y=710, width=1200, height=20)
    wall3 = Walls("Wall3", x=10, y=500, width=20, height=800)
    wall4 = Walls("Wall4", x=1190, y=500, width=20, height=800)
    wall5 = Walls("Wall5", x=200, y=510, width=370, height=20)
    wall6 = Walls("Wall6", x=690, y=190, width=20, height=180)

    for wall in [wall1, wall2, wall3, wall4, wall5, wall6]:
        passiveObjects.append(wall)
        wall.draw(canvas)

    count = Counter()

    for i in range(0,noOfBots):
        bot = Bot("Bot"+str(i),canvas, passiveObjects, count)
        brain = Brain(bot)
        bot.setBrain(brain)
        agents.append(bot)
        bot.draw(canvas)
    
    canvas.bind( "<Button-1>", lambda event: buttonClicked(event.x,event.y,agents) )
    
    return agents, passiveObjects, count

def moveIt(canvas,agents,passiveObjects,count,moves, timeOfDirt, draw_cam_line):
    for rr in agents:
        rr.thinkAndAct(agents,passiveObjects,canvas)
        rr.update(canvas,passiveObjects,1.0)
        if isinstance(rr,Bot):
            passiveObjects = rr.collectDirt(canvas,passiveObjects,count)
        moves +=1
        # Regenerate dirt every 10000 moves
        if moves % timeOfDirt == 0 and moves != 0:
            for i in range(300):
                dirt = Dirt(f"Dirt{moves}_{i}")  # unique name to avoid conflicts
                passiveObjects.append(dirt)
                dirt.draw(canvas)

    # Drawing Camera Line
    if draw_cam_line:
        drawAllCameraLines(canvas, agents)

    canvas.after(20,moveIt,canvas,agents,passiveObjects,count,moves, timeOfDirt, draw_cam_line)

# Adapt code from lab session
# Create by NattapongNEADTIP_20717335
def avoidRobots(canvas, listOfRobots, dt=1.0):
    for robot in listOfRobots:
        nearbyRobots = []
        for otherRobot in listOfRobots:
            d = robot.distance(otherRobot)
            if otherRobot != robot and d < 65:  # Threshold for avoidance
                nearbyRobots.append(otherRobot)

        # Compute separation force
        averageX = 0
        averageY = 0
        if nearbyRobots:
            for nb in nearbyRobots:
                differenceX = robot.x - nb.x
                differenceY = robot.y - nb.y
                distance = robot.distance(nb)
                if distance > 0:
                    averageX += differenceX / distance
                    averageY += differenceY / distance
            averageX /= len(nearbyRobots)
            averageY /= len(nearbyRobots)

            # Apply small steering adjustment
            angle = math.atan2(averageY, averageX)
            robot.theta = angle  # Face away from group
            robot.sl = 2.0
            robot.sr = 2.0

    # Move all robots after steering update
    for robot in listOfRobots:
        robot.move(canvas, dt)

    # Schedule next update
    canvas.after(20, avoidRobots, canvas, listOfRobots, dt)

def drawGrid(canvas, rows=12, cols=20, canvas_width=1200, canvas_height=720):
    cell_width = canvas_width // cols
    cell_height = canvas_height // rows
 
    # Draw vertical lines
    for i in range(cols + 1):
        x = i * cell_width
        canvas.create_line(x, 0, x, canvas_height)

    # Draw horizontal lines
    for j in range(rows + 1):
        y = j * cell_height
        canvas.create_line(0, y, canvas_width, y)

def drawAllCameraLines(canvas, agents):
    canvas.delete("view")  # Remove old lines

    for agent in agents:
        if isinstance(agent, Bot):

            agent.look(canvas, agents)


            radius = 30
            num_cameras = 30
            cam_start = -math.pi / 3
            cam_end = math.pi / 3
            for i in range(num_cameras):
                angle_offset = cam_start + i * (cam_end - cam_start) / (num_cameras - 1)
                angle = agent.theta + angle_offset
                cam_x = agent.x + radius * math.cos(angle)
                cam_y = agent.y + radius * math.sin(angle)
                canvas.create_line(cam_x, cam_y, cam_x + 200 * math.cos(angle), cam_y + 200 * math.sin(angle), fill="light grey", tags="view")


def main(noOfBots=1, noOfCats=1, amountOfDirt=1000, timeOfDirt = 1000, draw_cam_line =False, draw_grid=False):
    window = tk.Toplevel()
    canvas = initialise(window)
    agents, passiveObjects, count = createObjects(canvas,
                                                  noOfBots=noOfBots,
                                                  noOfLights=0,
                                                  amountOfDirt=amountOfDirt,
                                                  noOfCats=noOfCats)
    
    canvas.agents = agents
    
    if draw_cam_line:
        drawAllCameraLines(canvas, agents)

    if draw_grid:
        drawGrid(canvas)

    moveIt(canvas, agents, passiveObjects, count, 0, timeOfDirt=timeOfDirt, draw_cam_line=draw_cam_line)
    robotList = [a for a in agents if isinstance(a, Bot)]
    avoidRobots(canvas, robotList)



