import os
import csv
import numpy as np
import pandas as pd

from keras import optimizers
from keras.applications import vgg16, inception_v3, resnet50, mobilenet
from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from keras.models import Sequential, model_from_json, Model
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator

'''
DATA SETUP
'''
#resizing parameter 90x90 pixels, change to check the accuracy of the system
img_size = 90
batch_size = 32
train_samples_size = 10222

# Directories
training_dir = '../dataset/train'
testing_dir = '../dataset/test'

# TRAINING DATA
train_datagen = ImageDataGenerator(
  rescale=1./255,
  shear_range=0.2,
  zoom_range=0.2,
  horizontal_flip = True)

training_set = train_datagen.flow_from_directory(
  training_dir,
  target_size=(img_size, img_size),
  batch_size=batch_size,
  class_mode = 'categorical')

# TESTING DATA
test_datagen = ImageDataGenerator(rescale=1./255)

test_set = test_datagen.flow_from_directory(
  testing_dir,
  target_size=(img_size, img_size),
  batch_size=batch_size,
  class_mode = 'input')

'''
BUILD and FINE-TUNE THE MODEL
'''
#Load the VGG16 model
# - set include_top=False to not include the 3 fully-connected layers at the top of the network
# - reshape the input size to 90x90
vgg16_model = vgg16.VGG16(weights='imagenet', include_top=False, input_shape=(img_size,img_size,3))
# vgg16_model.summary(line_length=150)

flatten = Flatten()
# new_layer2 = Dense(120, activation='softmax')

vgg16_input = vgg16_model.input
vgg16_output = flatten(vgg16_model.output)
# out2 = new_layer2(flatten(vgg16_model.output))

mod_vgg16_model = Model(vgg16_input, vgg16_output)
# model2.summary(line_length=150)

# #Load the Inception_V3 model
# inception_model = inception_v3.InceptionV3(weights='imagenet')
 
# #Load the ResNet50 model
# resnet_model = resnet50.ResNet50(weights='imagenet')
 
# #Load the MobileNet model
# mobilenet_model = mobilenet.MobileNet(weights='imagenet')

# Transform VGG16 model into a Sequential model by adding its existing layers
model = Sequential()
for layer in mod_vgg16_model.layers:
  model.add(layer)

# Freeze the existing layers to prevent further training
for layer in model.layers:
  layer.trainable = False

# Add the last Dense layer to classify the number of required dog breeds
model.add(Dense(120, activation='softmax'))

'''
TRAIN THE FINE-TUNED MODEL
'''
# Compile the model
model.compile(
  optimizer = 'adam',
  loss = 'categorical_crossentropy',
  metrics = ['accuracy'])

epochs = 50
steps = train_samples_size // batch_size

# Fit the model
model.fit_generator(
  training_set,
  steps_per_epoch = steps,
  epochs = epochs,
  validation_data = test_set,
  validation_steps = 4)