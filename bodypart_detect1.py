# -*- coding: utf-8 -*-
"""bodypart_detect1.ipynb

Original file is located at
    https://colab.research.google.com/drive/1hASorPWfzVmdqbghag6M1WRpH2I621aG
"""

from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.optimizers import Adam

def dataset_processing(address):
    data = []
    for folder in os.listdir(address):
        folder = address + '/' + str(folder)
        if os.path.isdir(folder):
            for temp_part in os.listdir(folder):
                part = temp_part
                part_address = folder + '/' + str(temp_part)
                for temp_id in os.listdir(part_address):
                    id = temp_id
                    id_address = part_address + '/' + str(temp_id)
                    for temp_label in os.listdir(id_address):
                        if temp_label.split('_')[-1] == 'positive':
                            label = 'fractured'
                        elif temp_label.split('_')[-1] == 'negative':
                            label = 'normal'
                        else:
                            continue
                        label_address = id_address + '/' + str(temp_label)
                        for temp_image in os.listdir(label_address):
                            img_address = label_address + '/' + str(temp_image)
                            if img_address.lower().endswith(('.png', '.jpg', '.jpeg')):
                                data.append(
                                    {
                                        'Label': part,
                                        'Image_address': img_address
                                    }
                                )
    return data

Labels = ["ELBOW","FINGER","FOREARM","HAND","HUMERUS","SHOULDER", "WRIST"]

directory = r'/content/drive/MyDrive/radix/dataset' + '/MURA-v1.1'
dataset = dataset_processing(directory)

list_labels = []
list_paths = []
for row in dataset:
    list_labels.append(row['Label'])
    list_paths.append(row['Image_address'])

list_paths = pd.Series(list_paths, name='Path').astype(str)
list_labels = pd.Series(list_labels, name='Label')

image_data = pd.concat([list_paths, list_labels], axis=1)

data_train, data_test = train_test_split(image_data, train_size=0.9, shuffle=True, random_state=1)

data_train_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    horizontal_flip=True,
    preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
    validation_split=0.2
)

def my_image_generator(generator, dataframe, **kwargs):
    import PIL
    while True:
        try:
            for x, y in generator.flow_from_dataframe(dataframe, **kwargs):
                yield x, y
        except PIL.UnidentifiedImageError as e:
            print(f"Error loading image: {e}")

train_data = my_image_generator(
    data_train_generator,
    dataframe=data_train,
    x_col='Path',
    y_col='Label',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=64,
    shuffle=True,
    seed=42,
    subset='training'
)

val_data = my_image_generator(
    data_train_generator,
    dataframe=data_train,
    x_col='Path',
    y_col='Label',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=64,
    shuffle=True,
    seed=42,
    subset='validation'
)

data_test_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=tf.keras.applications.resnet50.preprocess_input
)

test_data = data_test_generator.flow_from_dataframe(
    dataframe=data_test,
    x_col='Path',
    y_col='Label',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    shuffle=False
)

train_steps_per_epoch = len(data_train) // 64
val_steps_per_epoch = len(data_train) // 64

num_classes = len(Labels)
pretrained_model = tf.keras.applications.resnet50.ResNet50(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)

pretrained_model.trainable = False

inputs = pretrained_model.input
x = tf.keras.layers.Dense(128, activation='relu')(pretrained_model.output)
x = tf.keras.layers.Dense(50, activation='relu')(x)
outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
model = tf.keras.Model(inputs, outputs)

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

callbacks = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
history = model.fit(
    train_data,
    validation_data=val_data,
    steps_per_epoch=train_steps_per_epoch,
    validation_steps=val_steps_per_epoch,
    epochs=8,
    callbacks=[callbacks]
)