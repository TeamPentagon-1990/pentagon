# -*- coding: utf-8 -*-
"""testcase_Run.ipynb

Original file is located at
    https://colab.research.google.com/drive/1lYJgpRsswBSzmMqRRzLx9BGP6bCch4yn
"""

from google.colab import drive
drive.mount('/content/drive')

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

model_path = '/content/drive/MyDrive/model/fracture_detectionXR_ELBOW_frac.h5'
model = load_model(model_path)

def load_and_preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Rescale as done during training
    return img_array

# Example usage
img_path = '/content/drive/MyDrive/custom_input/Copy of image2.png'
new_image = load_and_preprocess_image(img_path)
prediction = model.predict(new_image)

# Interpret the prediction
predicted_class = np.argmax(prediction[0])
if predicted_class == 1:
    print("The bone is fractured.")
else:
    print("The bone is not fractured.")