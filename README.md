# Automomus vehicle simulation
Data collection and training on CARLA simulator.

## background
The concept of driverless cars has been becoming more and more attractive in modern society. With the artificial driver assistants, people are benefited from getting rid of concentrating on the road throughout the whole trip and utilize the time to focus on other tasks. On the other hand, it could reduce the accident rate with the mature autopilots that are capable of responding to various road situations rapidly. </br>
This project builds a virtual environment on CARLA which is an open-source autonomous driving simulator. It captures images from artificial cameras on the vehicles. It not only allows collecting the data in a safe way but also increasing the variety of the dataset since the environment conditions can be adjusted in the simulator. Currently, with data and features like daylight, road signs, signals, weather and road situations parsed into the model, it identifies the situation that the car will bump into obstacles, then the model generates a triplet as output to the car simulation to avoid car crashes. After experiments and evaluation, the model successfully processed data and features in normal driving situations like road sign (tracks), traffic light, daylight. The model then successfully parses the result into the car simulation that supports speed (60km/h) steadily.

## Data collection
The data used in the driverless automobile system comes from the CARLA car simulator. CARLA simulator simulates real life driving experience, with varied daylight, spawn position of vehicle, weather, road situation (driveway signs and signals like traffic light), and so on. It also provides easy access to maps and navigation with an user-friendly Python API, to toggle environment objects and navigate through lanes or waypoints. The description of data is divided into data collection, data loader. </br>

### Script for collecting autopilot data
#### 1. Start the simulator
Installed and launch CARLA simulator beforehand. <br />
CARLA 0.9.5 is used and you can select your own version. <br>
Installation guide for CARLA can be found [here](https://carla.readthedocs.io/en/latest/start_quickstart/).

#### 2. Run the python script to enable data collection
Run `data_collection.py` to collect images. <br />

### Data collection method
- The vehicle is spawned in a random position of the map, with commands sent to CARLA simulator.
- The vehicle moves in autopilot mode to collect front camera images with fps specified by the user. (In this case, it is specified that the front camera to capture RGB images in 2 fps, normalized by the RGB color range (255).)  
- The data collection is applied on seven maps in CARLA's default non-layered maps, denoted from Town01 to Town07. Each town contains different features such as Tjunctions, highways and rural roads. During collecting data, the vehicle drives for 600 seconds in each map, which captures a total of 1200 images per map, which means the total data set consists of 1200 * 7 images. 
- An addition feature and variation added to make the model more robust is the dynamic weather feature, it is applied on each map, different weather and daylight situation is resulted, for example, sunny, rainy, morning, night, etc, which increases the variation of data and prevent the model from over-fitting the collected data set. <br/>
Examples of different driving scenarios. <br/>
![](/media/front_cam.png)
- The data collected are divided into batches, each with 8 images and their labels in a npz file, the label is a list of three components, consisting of throttle, steer and brake control of the frame that the model predicted in order to avoid car crashes.
-  80\% data is used as training data and the rest 20\% is used as model validation. Each npz file is extracted into data and label, then image resize is applied to all dataset for later image processing purpose. Eventually, all images and labels are appended into X and y arrays respectively for model training.

## Training
### Image preprocessing
- Resize: The image is resized from (680, 480) to (160, 120). An image of lower resolution will be able to provide enough information for training while shorten the training time.
- Normalization: The image is 8 bit RGB images. We will normalize it into a range of [0,1] by dividing each pixel by 255. Normalized data will increase the stability of the network and converge faster.
### CNN Model
A CNN model is used in training. Architecture is shown as below. <br>
![](/media/model.png)<br />
### Script for training
A deep convolutional neural network is used in the training in `model.ipynb`. The trained model will be saved as `CNN_model`. <br>
The accuracy and loss plot. <br />
![](/media/acc_loss.png)<br />

## Deploying on CARLA
### Result
![](/media/res.gif)
### Script for deploying in CARLA
The trained model can be launched in the CARLA simulator by running `test.py` <br>
Learning rate of \(10^{-5}\) and batch size of 32 were used while training and testing. <br>
It has reached 94\% in training accuracy with 0.0297 loss and 0.8902 in validation accuracy with 0.0533 loss. In testing, it achieved 0.8793 accuracy on unseen data, indicating a good generalization ability. <br>

## Visualization of activation maps
To have a better understanding regarding how CNN is extracting the features, I visualize the internal activation maps of the first two convolutional layers inside the network which contains a highway road, with no advanced image processing is fed into the neural network. After passing through the convolutional layers, the first two activations are captured. The outline of the road is shown clearly, indicating the ability of CNN to learn useful convolutional filters by itself. 
Activation map of the first convolutional layer <br />
![image](/media/activation_1.png)<br />
Activation map of the second convolutional layer <br />
![image](/media/activation_2.png)<br />

