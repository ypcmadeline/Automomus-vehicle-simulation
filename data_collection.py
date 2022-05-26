import glob
import os
import sys
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla
import random
import time
import numpy as np
import cv2
import math


class CarEnv:

    # settings
    # town = 'Town02'
    im_width = 640
    im_height = 480

    def __init__(self, town):
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.town = town
        # self.world = self.client.get_world()
        self.world = self.client.load_world(self.town)
        # self.change_map('Town05')
        self.blueprint_library = self.world.get_blueprint_library()
        self.traffic_manager = self.client.get_trafficmanager(8000)

        self.collided = False
        self.images = []       
        self.actor_list = []
        self.count = 0
        self.batch_size = 8
        self.store = 0
        self.x = []
        self.y = []
        self.path = 'dataset/test/'
        self.collision_hist = []

    def process_img(self, image):
        i = np.array(image.raw_data)
        i2 = i.reshape((self.im_height, self.im_width, 4))
        i3 = i2[:, :, :3]
        self.images.append(i3)
        cv2.imwrite(f"img/{self.town}/test{self.count}.jpg", i3)
        self.count += 1
        return i3/255.0

    def set_vehicles(self):
        self.model_3 = self.blueprint_library.filter('model3')[0]

        self.transform = random.choice(self.world.get_map().get_spawn_points())
        self.vehicle = self.world.spawn_actor(self.model_3, self.transform)
        self.change_vehicle_speed(-300) # 20*300% = 60kmh
        self.actor_list.append(self.vehicle)

        self.rgb_cam = self.world.get_blueprint_library().find('sensor.camera.rgb')

        self.rgb_cam.set_attribute('image_size_x', f'{self.im_width}')
        self.rgb_cam.set_attribute('image_size_y', f'{self.im_height}')
        self.rgb_cam.set_attribute('fov', '110')
        self.rgb_cam.set_attribute('sensor_tick', '0.5')

        transform = carla.Transform(carla.Location(x=2.5, z=0.7))

        self.sensor = self.world.spawn_actor(self.rgb_cam, transform, attach_to=self.vehicle)

        self.actor_list.append(self.sensor)
        self.sensor.listen(lambda data: self.save_dataset(data))

        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0))

        time.sleep(4) # sleep to get things started and to not detect a collision when the car spawns/falls from sky.

        colsensor = self.world.get_blueprint_library().find('sensor.other.collision')
        self.colsensor = self.world.spawn_actor(colsensor, transform, attach_to=self.vehicle)
        self.actor_list.append(self.colsensor)
        self.colsensor.listen(lambda event: self.collision_data(event))


        self.vehicle.set_autopilot(True) # 20km/h



    def drive(self, duration):
        CARLA.set_vehicles()
        time.sleep(duration)

    def collision_data(self, event):
        self.collision_hist.append(event)
        self.collided = True
        print("collided")
        print(event)

    def save_dataset(self, img):
        image = self.process_img(img)
        control = self.vehicle.get_control()
        label_list = [control.throttle, control.steer, control.brake]
        label = np.array(label_list)

        v = self.vehicle.get_velocity()
        kmh = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)

        v = self.vehicle.get_velocity()
        if self.store < self.batch_size:
            self.x.append(image)
            self.y.append(label)
            self.store += 1
        else:
            self.x = np.array(self.x)
            # print(self.x.shape)
            self.y = np.array(self.y)
            # print(self.y.shape)
            np.savez(f"dataset/{self.town}/{self.count}", x=self.x, y=self.y)
            self.x = []
            self.y = []
            self.store = 0
        
        
    def change_vehicle_speed(self, percentage):
        self.traffic_manager.global_percentage_speed_difference(percentage)

    def change_map(self, map):
        self.world = self.client.load_world(map)

    
maps = ['Town01','Town02','Town03''Town04','Town05','Town06','Town07']   
for map in maps: 
    CARLA = CarEnv(map)
    CARLA.drive(600)

