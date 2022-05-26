import cv2
import numpy as np
import glob
import tensorflow as tf
from sklearn.model_selection import train_test_split
import time

# datafolder = "dataset/test"
SPLIT_SIZE = 0.2

class data_loader:
    def __init__(self):
        self.x = []
        self.y = []
        self.batch_size = 8


    def load_data(self, path):
        with tf.device('/gpu:0'):
            print("Loading "+path)
            for np_name in glob.glob(path+'/*.np[yz]'):
                data = np.load(np_name)
                for i in range(self.batch_size):
                    resized = cv2.resize(data["x"][i], (160, 120), interpolation = cv2.INTER_AREA)   # 680/4, 480/4
                    resized = resized.astype(np.float16)
                    cv2.imwrite("resized.jpg", data["x"][i])
                    # break
                    try:
                        x = tf.constant(resized)
                        y = tf.constant(data["y"][i])
                        self.x.append(x)
                        self.y.append(y)
                    except:
                        pass


    def tf_dataset(self):
        # self.x = np.array(self.x)
        # self.y = np.array(self.y)
        train_images, test_images, train_labels, test_labels = train_test_split(self.x, self.y, test_size=SPLIT_SIZE)
        return train_images, test_images, train_labels, test_labels

# start = time.time()
# dl = data_loader()
# dl.load_data("dataset/Town01")
# dl.load_data("dataset/Town02")
# dl.load_data("dataset/Town03")
# dl.load_data("dataset/Town04")
# dl.load_data("dataset/Town05")
# dl.tf_dataset()
# end = time.time()
# print(end - start)

