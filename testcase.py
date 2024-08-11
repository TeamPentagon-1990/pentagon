import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image

# Load the model
model_path = '/Users/girivasanthvm/Documents/python/fracture_detectionXR_SHOULDER_frac.h5'
model = load_model(model_path)

# Streamlit file uploader for image upload
uploaded_file = st.file_uploader("Choose a JPG image...", type="jpg")

if uploaded_file is not None:
    # Open the uploaded image file as a PIL image
    img = Image.open(uploaded_file)

    # Display the uploaded image in Streamlit
    st.image(img, caption='Uploaded Image', use_column_width=True)

# Resize the image to 224x224 
    # Preprocess the image
    img = img.resize((224, 224))  # Resize the image to match model's input size
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Rescale as done during training

    # Make prediction
    predictions = model.predict(img_array)
    predicted_class = np.argmin(predictions[0])
    if predicted_class == 1:
        st.write("The bone is fractured.")
    else:
        st.write("The bone is not fractured.")