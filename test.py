import glob
import os
import sys
import random
import time
import numpy as np
import cv2
import math
import subprocess
from keras.models import load_model

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla')
except IndexError:
    pass

import carla
from agents.navigation.global_route_planner import GlobalRoutePlanner



class CarEnv:

    def __init__(self, model):
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.town = "Town01"
        # self.world = self.client.get_world()
        self.world = self.client.load_world(self.town)
        # self.change_map('Town05')
        self.blueprint_library = self.world.get_blueprint_library()
        self.traffic_manager = self.client.get_trafficmanager(8000)

        self.im_width = 640
        self.im_height = 480

        self.collided = False
        self.images = []       
        self.actor_list = []
        self.count = 0
        self.batch_size = 8
        self.store = 0
        self.x = []
        self.y = []
        self.collision_hist = []

        self.model = model

    def process_img(self, image):
        i = np.array(image.raw_data)
        i2 = i.reshape((self.im_height, self.im_width, 4))
        i3 = i2[:, :, :3]
        cv2.imwrite(f"Testing/test{self.count}.jpg", i3)
        self.count += 1
        return i3/255.0

    def decide(self, img):
        image = self.process_img(img)
        resized = cv2.resize(image, (160, 120), interpolation = cv2.INTER_AREA)   # 680/4, 480/4
        image = resized.astype(np.float16)
        image = image.reshape(1,120,160,3)
        out = self.model.predict(image)
        print(out)
        self.step(out[0])
        return out

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
        self.sensor.listen(lambda data: self.decide(data))

        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0))

        time.sleep(4) # sleep to get things started and to not detect a collision when the car spawns/falls from sky.

        colsensor = self.world.get_blueprint_library().find('sensor.other.collision')
        self.colsensor = self.world.spawn_actor(colsensor, transform, attach_to=self.vehicle)
        self.actor_list.append(self.colsensor)
        self.colsensor.listen(lambda event: self.collision_data(event))


    def collision_data(self, event):
        self.collision_hist.append(event)

    def change_vehicle_speed(self, percentage):
        self.traffic_manager.global_percentage_speed_difference(percentage)
    
    def step(self, action):
        t = float(round(action[0],2))
        b = float(round(action[1],2))
        s = float(round(action[2],2))
        self.vehicle.apply_control(carla.VehicleControl(throttle=t,
                                                        brake=b,
                                                        steer=s))
        v = self.vehicle.get_velocity()
        kmh = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)
        print(f"velocity: {kmh}")

    

if __name__ == '__main__':
    model = load_model("CNN_model")
    print(model.summary())
    # Clear Carla Environment
    # print('### Reseting Carla Map ###')
    # os.system('python3 ' + settings.path2CARLA + 'PythonAPI/util/config.py -m ' + str(settings.CARLA_MAP))
    os.chdir("/home/ypchanai/carla-simulator")
    os.system("cd ~/carla-simulator")
    p = subprocess.Popen("DISPLAY=:8 vglrun -d :7.1 ./CarlaUE4.sh -carla-streaming-port=0", shell=True)
    time.sleep(5)
    env = CarEnv(model)
    env.set_vehicles()



