import os
import sys
from PIL import Image, ImageTk

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

# class AirConditioner(Device):
#     def __init__(self, name):
#         super().__init__(name)
#         self.is_on = False
#         self.temperature = 22  # Example temperature attribute

#     def draw(self, canvas, image_cache, x, y):
#         """在canvas上绘制家电的图片和状态"""
#         img = image_cache.get('ac')
#         if not img:
#             img = Image.open("environment/images/ac.png").resize((50, 50))
#             image_cache['ac'] = ImageTk.PhotoImage(img)

#         canvas.create_image(x, y, image=image_cache['ac'], tags=self.name)
#         status_text = f"{self.name}: {'on' if self.is_on else 'off'} {self.temperature}"
#         canvas.create_text(x + 60, y, text=status_text, tags="appliance_status", anchor="w", font=("Arial", 10))

# class AirPurifier(Device):
#     def __init__(self, name):
#         super().__init__(name)
#         self.is_on = False

#     def draw(self, canvas, image_cache, x, y):
#         img = image_cache.get('purifier')
#         if not img:
#             img = Image.open("environment/images/purifier.png").resize((50, 50))
#             image_cache['purifier'] = ImageTk.PhotoImage(img)

#         canvas.create_image(x, y, image=image_cache['purifier'], tags=self.name)
#         status_text = f"{self.name}: {'on' if self.is_on else 'off'}"
#         canvas.create_text(x + 60, y, text=status_text, tags="appliance_status", anchor="w", font=("Arial", 10))

class DrawableMixin:
    def __init__(self, x, y, width=50, height=50, image=None):
        self.centreX = x
        self.centreY = y
        self.width = width
        self.height = height
        self.image = image  # tkinter的PhotoImage对象
        self._canvas_items = {}  # 记录canvas上画的元素，方便后续更新

    def draw(self, canvas):
        """在canvas上绘制自己，包括图片和状态文字"""
        x1 = self.centreX - self.width // 2
        y1 = self.centreY - self.height // 2
        x2 = self.centreX + self.width // 2
        y2 = self.centreY + self.height // 2

        # 如果之前画过，需要先删掉（避免叠图）
        if self._canvas_items:
            for item in self._canvas_items.values():
                canvas.delete(item)
            self._canvas_items.clear()

        # 画图片
        if self.image:
            img_item = canvas.create_image(self.centreX, self.centreY, image=self.image, tags=self.name)
        else:
            img_item = canvas.create_rectangle(x1, y1, x2, y2, fill="gray", tags=self.name)

        # 画状态文字
        status_text = self.get_status_text()  # 让子类/主类提供状态字符串
        text_item = canvas.create_text(self.centreX + self.width, 
                                       self.centreY, 
                                       text=status_text, 
                                       tags="appliance_status",
                                       anchor="w", 
                                       font=("Arial", 10))

        # 记录item
        self._canvas_items['image'] = img_item
        self._canvas_items['text'] = text_item


    def get_status_text(self):
        """返回当前设备/传感器的状态文本。默认返回名字。子类可以override。"""
        return self.name

class DrawableAirConditioner(AirConditioner, DrawableMixin):
    def __init__(self, name, device: AirConditioner, x, y, image=None):
        self.device = device
        AirConditioner.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        DeviceManager.register_device(self)

    def get_status_text(self):
        """自定义状态文本，比如温度"""
        return f"{self.name}: {'on' if self.is_on else 'off'} {self.temperature}"

class DrawableAirPurifier(AirPurifier, DrawableMixin):
    def __init__(self, name, device:AirPurifier, x, y, image=None):
        self.device = device
        AirPurifier.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        DeviceManager.register_device(self)

    def get_status_text(self):
        """返回净化器状态"""
        return f"{self.name}: {'on' if self.is_on else 'off'}"

class DrawableBlind(Blind, DrawableMixin):
    def __init__(self, name, device: Blind, x, y, image=None):
        self.device = device
        Blind.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        DeviceManager.register_device(self)

    def get_status_text(self):
        """返回百叶窗开合度"""
        return f"{self.name}: {self.level}%"

class DrawableCurtain(Curtain, DrawableMixin):
    def __init__(self, name, device: Curtain, x, y, image=None):
        self.device = device
        Curtain.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        DeviceManager.register_device(self)

    def get_status_text(self):
        """返回窗帘状态"""
        return f"{self.name}: {'open' if self.is_open else 'closed'}"

class DrawableLight(Light, DrawableMixin):
    def __init__(self, name, device: Light, x, y, image=None):
        self.device = device
        Light.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        DeviceManager.register_device(self)

    def get_status_text(self):
        """返回灯光亮度"""
        return f"{self.name}: {self.brightness}%"

class DrawableTV(TV, DrawableMixin):
    def __init__(self, name, device: TV, x, y, image=None):
        self.device = device
        TV.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        DeviceManager.register_device(self)
        print(DeviceManager._devices)

    def get_status_text(self):
        """返回电视状态"""
        return f"{self.name}: {'on' if self.is_on else 'off'}"

class DrawableWindow(Window, DrawableMixin):
    def __init__(self, name, device: Window, x, y, image=None):
        self.device = device
        Window.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        DeviceManager.register_device(self)

    def get_status_text(self):
        """返回窗户状态"""
        return f"{self.name}: {'open' if self.is_open else 'closed'}"

class DrawableIndoorTempSensor(IndoorTempSensor, DrawableMixin):
    def __init__(self, name, device: IndoorTempSensor, x, y, image=None):
        self.device = device
        IndoorTempSensor.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        SensorManager.register_sensor(self)

    def get_status_text(self):
        """返回室内温度"""
        return f"{self.name}: {self.get_status()}{self.unit}"

class DrawableOutdoorTempSensor(OutdoorTempSensor, DrawableMixin):
    def __init__(self, name, device: OutdoorTempSensor, x, y, image=None):
        self.device = device
        OutdoorTempSensor.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        SensorManager.register_sensor(self)

    def get_status_text(self):
        """返回室外温度"""
        return f"{self.name}: {self.get_status()}{self.unit}"

class DrawablePowerMeter(PowerMeter, DrawableMixin):
    def __init__(self, name, device: PowerMeter, x, y, image=None):
        self.device = device
        PowerMeter.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        SensorManager.register_sensor(self)

    def get_status_text(self):
        """返回当前耗电量"""
        return f"{self.name}: {self.get_status()}{self.unit}"

class DrawableRainSensor(RainSensor, DrawableMixin):
    def __init__(self, name, device: RainSensor, x, y, image=None):
        self.device = device
        RainSensor.__init__(self, name)
        DrawableMixin.__init__(self, x, y, image=image)
        SensorManager.register_sensor(self)

    def get_status_text(self):
        """返回当前降雨量"""
        return f"{self.name}: {self.get_status()}{self.unit}"

def draw_appliances(canvas, image_cache, appliances):
    canvas.delete("appliance_status")

    # 加载家电和传感器图片
    ac_img = Image.open("environment/images/ac.png").resize((50, 50))
    purifier_img = Image.open("environment/images/purifier.png").resize((50, 50))
    curtain_img = Image.open("environment/images/curtain.png").resize((50, 50))
    blind_img = Image.open("environment/images/blind.png").resize((50, 50))
    light_img = Image.open("environment/images/light.png").resize((50, 50))
    tv_img = Image.open("environment/images/tv.png").resize((50, 50))
    window_img = Image.open("environment/images/window.png").resize((50, 50))
    temp_img = Image.open("environment/images/temp.png").resize((50, 50))
    power_img = Image.open("environment/images/power.png").resize((50, 50))
    rain_img = Image.open("environment/images/rain.png").resize((50, 50))

    # 转换为Tkinter PhotoImage对象
    ac_photo = ImageTk.PhotoImage(ac_img)
    purifier_photo = ImageTk.PhotoImage(purifier_img)
    curtain_photo = ImageTk.PhotoImage(curtain_img)
    blind_photo = ImageTk.PhotoImage(blind_img)
    light_photo = ImageTk.PhotoImage(light_img)
    tv_photo = ImageTk.PhotoImage(tv_img)
    window_photo = ImageTk.PhotoImage(window_img)
    temp_photo = ImageTk.PhotoImage(temp_img)
    power_photo = ImageTk.PhotoImage(power_img)
    rain_photo = ImageTk.PhotoImage(rain_img)

    # 存储图片引用防止被垃圾回收
    image_cache["ac"] = ac_photo
    image_cache["purifier"] = purifier_photo
    image_cache["curtain"] = curtain_photo
    image_cache["blind"] = blind_photo
    image_cache["light"] = light_photo
    image_cache["tv"] = tv_photo
    image_cache["window"] = window_photo
    image_cache["temp"] = temp_photo
    image_cache["power"] = power_photo
    image_cache["rain"] = rain_photo

    devices, sensors = appliances

    # 设置家电和传感器的绘制位置和图片
    positions = {
        'living_room_ac': (1250, 100, ac_photo),
        'bedroom_ac': (1250, 140, ac_photo),
        'main_purifier': (1250, 180, purifier_photo),
        'living_room_curtain': (1250, 220, curtain_photo),
        'kitchen_blind': (1250, 260, blind_photo),
        'kitchen_light': (1250, 300, light_photo),
        'bedroom_light': (1250, 340, light_photo),
        'hallway_light': (1250, 380, light_photo),
        'living_room_tv': (1250, 420, tv_photo),
        'bathroom_window': (1250, 460, window_photo),
        'bedroom_window': (1250, 520, window_photo),
        'indoor_temp_sensor': (1250, 560, temp_photo),
        'outdoor_temp_sensor': (1250, 600, temp_photo),
        'main_power_meter': (1250, 640, power_photo),
        'rain_sensor': (1250, 680, rain_photo)
    }

    drawable_devices = []

    # 为每个设备创建可绘制包装器
    for device in devices + sensors:
        if device.name in positions:
            x, y, img = positions[device.name]

            # 根据设备类型创建对应的Drawable包装器
            if isinstance(device, AirConditioner):
                drawable = DrawableAirConditioner(device.name, device, x, y, img)
            elif isinstance(device, AirPurifier):
                drawable = DrawableAirPurifier(device.name, device, x, y, img)
            elif isinstance(device, Blind):
                drawable = DrawableBlind(device.name, device, x, y, img)
            elif isinstance(device, Curtain):
                drawable = DrawableCurtain(device.name, device, x, y, img)
            elif isinstance(device, Light):
                drawable = DrawableLight(device.name, device, x, y, img)
            elif isinstance(device, TV):
                drawable = DrawableTV(device.name, device, x, y, img)
            elif isinstance(device, Window):
                drawable = DrawableWindow(device.name, device, x, y, img)
            elif isinstance(device, IndoorTempSensor):
                drawable = DrawableIndoorTempSensor(device.name, device, x, y, img)
            elif isinstance(device, OutdoorTempSensor):
                drawable = DrawableOutdoorTempSensor(device.name, device, x, y, img)
            elif isinstance(device, PowerMeter):
                drawable = DrawablePowerMeter(device.name, device, x, y, img)
            elif isinstance(device, RainSensor):
                drawable = DrawableRainSensor(device.name, device, x, y, img)
            else:
                continue

            # 复制设备状态到drawable包装器
            for attr, value in device.__dict__.items():
                if not attr.startswith('_'):
                    setattr(drawable, attr, value)

            drawable_devices.append(drawable)

    # 绘制所有包装后的设备，并添加到 drawn_items 中
    for device in drawable_devices:
        device.draw(canvas)
    
    return drawable_devices

def update_appliance_status(canvas, appliances, drawable_devices):
    # Update the status of each device and redraw
    for device in appliances[0] + appliances[1]:
        drawable = find_drawable_for_device(device, drawable_devices)
        if drawable:
            # Update device status
            for attr, value in device.__dict__.items():
                if not attr.startswith('_'):
                    setattr(drawable, attr, value)
            # Redraw the device with updated state
            drawable.draw(canvas)

def find_drawable_for_device(device, drawable_devices):
    # Logic to find the drawable object for a given device
    for drawable in drawable_devices:
        if drawable.device == device:
            return drawable
    return None
