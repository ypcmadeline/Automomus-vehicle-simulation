# CNN_self_driving_on_carla
Data collection and training with CNN on Carla simulator.

## Data collection
Launch carla simulator beforehand. <br />
Run `data_collection.py` to collect images. <br />
A front camera is attached to a vehicle and the vehicle is driven under autopilot mode. Time-stamped images and corresponding driving behavior are collected in the meantime. To increase the diversity of the data, different weather and daylight condition are applied in the simulation. <br />
![image](https://github.com/ypcmadeline/CNN_self_driving_on_carla/blob/main/media/front_cam.png)<br />
The data collection is launched on 7 different maps.

## Training
![image](https://github.com/ypcmadeline/CNN_self_driving_on_carla/blob/main/media/model.png)<br />
A deep convolutional neural network is used in the training in `model.ipynb`. The trained model will be saved as `CNN_model`.
The accuracy and loss plot. <br />
![image](https://github.com/ypcmadeline/CNN_self_driving_on_carla/blob/main/media/acc_loss.png)<br />

## Visualization of activation maps
Activation map of the first convolutional layer <br />
![image](https://github.com/ypcmadeline/CNN_self_driving_on_carla/blob/main/media/activation_1.png)<br />
Activation map of the second convolutional layer <br />
![image](https://github.com/ypcmadeline/CNN_self_driving_on_carla/blob/main/media/activation_2.png)<br />

## Testing
The trained model can be launched in the Carla simulator by running `test.py`
