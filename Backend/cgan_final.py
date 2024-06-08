# -*- coding: utf-8 -*-
"""cgan_final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1W4Ub-iT_c0F3K8AZkbPKolrpl5--wx6Y
"""

from google.colab import drive
drive.mount('/content/drive')

!cp -r /content/drive/MyDrive/maps.zip /content

!unzip maps.zip

from glob import glob
import time
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import Sequential
from keras.layers import Conv2D, Input, MaxPool2D, Conv2DTranspose, concatenate, BatchNormalization, Activation, LeakyReLU, ReLU
from keras.models import Model
from keras.utils import img_to_array, load_img,plot_model
from keras.optimizers import Adam
from keras.initializers import RandomNormal
from keras.layers import Dropout, Lambda
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, accuracy_score
import seaborn as sns
from glob import glob
from sklearn.model_selection import train_test_split

path = "maps/train/"
num_images = 1000

combined_images = sorted(glob(path + "*.jpg"))[:num_images]

images = np.zeros(shape=(len(combined_images), 256, 256, 3))
masks = np.zeros(shape=(len(combined_images), 256, 256, 3))


for idx, path in enumerate(combined_images):

    combined_image = tf.cast(img_to_array(load_img(path)), tf.float32)

    image = combined_image[:,:600,:]
    mask = combined_image[:,600:,:]

    images[idx] = (tf.image.resize(image,(256,256)))/255
    masks[idx] = (tf.image.resize(mask,(256,256)))/255

plt.figure(figsize=(25,10))
for i in range(1,6):
    idx = np.random.randint(1,1000)
    image, mask = images[idx], masks[idx]
    plt.subplot(2,5,i)
    plt.imshow(image)
    plt.savefig("/content/drive/MyDrive/image.jpg")
    plt.title(str(i) + " .Satellite image")
    plt.axis("off")
    plt.subplot(2,5,i + 5)
    plt.imshow(mask)
    plt.title(str(i) + " .Map ")
    plt.axis("off")
plt.show()

# Data augmentation
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest'
)

import matplotlib.pyplot as plt
# Generate augmented images
train_generator = datagen.flow(x_train, y_train, batch_size=32)
augmented_images, _ = next(train_generator)
# Display the first few augmented images
plt.figure(figsize=(10, 10))
for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(augmented_images[i])
    plt.axis("off")
plt.show()

x_train, x_test, y_train, y_test = train_test_split(images, masks, test_size=0.1, random_state=42)

from keras.layers import MaxPooling2D
input_img = Input(shape=(256, 256, 3))
s = Lambda(lambda x: x / 255)(input_img)
c1 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(s)
c1 = Dropout(0.1)(c1)
c1 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c1)
p1 = MaxPooling2D((2, 2))(c1)
u9 = Conv2DTranspose(16, (2, 2), strides=(2, 2), padding='same')(p1)
u9 = concatenate([u9, c1], axis=3)
c9 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u9)
c9 = Dropout(0.1)(c9)
c9 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c9)
outputs = Conv2D(1, (1, 1), activation='sigmoid')(c9)

# Define the Pix2Pix Generator
def downscale(filters, kernel_size=4, apply_batchnorm=True):
    initializer = tf.random_normal_initializer(0., 0.02)
    result = Sequential()
    result.add(Conv2D(filters, kernel_size, strides=2, padding='same',
                      kernel_initializer=initializer, use_bias=not apply_batchnorm))
    if apply_batchnorm:
        result.add(BatchNormalization())
    result.add(LeakyReLU())
    return result

def upscale(filters, kernel_size=4, apply_dropout=False):
    initializer = tf.random_normal_initializer(0., 0.02)
    result = Sequential()
    result.add(Conv2DTranspose(filters, kernel_size, strides=2, padding='same',
                               kernel_initializer=initializer, use_bias=False))
    result.add(BatchNormalization())
    if apply_dropout:
        result.add(Dropout(0.5))
    result.add(ReLU())
    return result

def Generator():
    inputs = Input(shape=[256, 256, 3])

    down_stack = [
        downscale(64, apply_batchnorm=False),
        downscale(128),
        downscale(256),
        downscale(512),
        downscale(512),
        downscale(512),
        downscale(512),
        downscale(512)
    ]

    up_stack = [
        upscale(512, apply_dropout=True),
        upscale(512, apply_dropout=True),
        upscale(512, apply_dropout=True),
        upscale(512),
        upscale(256),
        upscale(128),
        upscale(64)
    ]

    initializer = RandomNormal(stddev=0.02)
    last = Conv2DTranspose(3, kernel_size=4, strides=2, padding="same",
                           kernel_initializer=initializer, activation="tanh")

    x = inputs
    skips = []
    for down in down_stack:
        x = down(x)
        skips.append(x)

    skips = reversed(skips[:-1])

    for up, skip in zip(up_stack, skips):
        x = up(x)
        x = concatenate([x, skip])

    x = last(x)

    return Model(inputs=inputs, outputs=x)

generator = Generator()

plot_model(generator)

def Discriminator():
    image = Input(shape = (256,256,3), name = "ImageInput")
    target = Input(shape = (256,256,3), name = "TargetInput")
    x = concatenate([image, target])

    x = downscale(64)(x)
    x = downscale(128)(x)
    x = downscale(512)(x)

    initializer = RandomNormal(stddev = 0.02, seed=42)

    x = Conv2D(512, kernel_size = 4, strides = 1, kernel_initializer = initializer, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = LeakyReLU()(x)

    x = Conv2D(1, kernel_size = 4, kernel_initializer = initializer)(x)

    discriminator = Model(inputs = [image, target], outputs = x, name = "Discriminator")

    return discriminator

discriminator = Discriminator()

plot_model(discriminator)

adversarial_loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
generator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
discriminator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
def generator_loss(discriminator_generated, generated_output, target_image):
    gan_loss = adversarial_loss(tf.ones_like(discriminator_generated), discriminator_generated)
    l1_loss = tf.reduce_mean(tf.abs(target_image - generated_output))
    total_loss = (100 * l1_loss) + gan_loss
    return total_loss, gan_loss, l1_loss
def discriminator_loss(discriminator_real_output, discriminator_generated_output):
    real_loss = adversarial_loss(tf.ones_like(discriminator_real_output), discriminator_real_output)
    fake_loss = adversarial_loss(tf.zeros_like(discriminator_generated_output), discriminator_generated_output)
    total_loss = real_loss + fake_loss
    return total_loss
def train_step(inputs, target):
    with tf.GradientTape() as generator_tape, tf.GradientTape() as discriminator_tape:
        generated_output = generator(inputs, training=True)

        discriminator_real_output = discriminator([inputs, target], training=True)
        discriminator_generated_output = discriminator([inputs, generated_output], training=True)

        generator_total_loss, generator_gan_loss, generator_l1_loss = generator_loss(discriminator_generated_output, generated_output, target)

        discriminator_Loss = discriminator_loss(discriminator_real_output, discriminator_generated_output)

    generator_gradients = generator_tape.gradient(generator_total_loss, generator.trainable_variables)
    generator_optimizer.apply_gradients(zip(generator_gradients, generator.trainable_variables))

    discriminator_gradients = discriminator_tape.gradient(discriminator_Loss, discriminator.trainable_variables)
    discriminator_optimizer.apply_gradients(zip(discriminator_gradients, discriminator.trainable_variables))

def fit(data, epochs):
    for epoch in range(epochs):
        start = time.time()
        print("Current epoch: ", epoch+1)
        for image, mask in data:
            train_step(image, mask)
        print(f"Time taken to complete the epoch {epoch + 1} is {(time.time() - start):.2f} seconds \n")

sat_image, map_image = tf.cast(images, tf.float32), tf.cast(masks, tf.float32)
dataset = (sat_image,map_image)
data = tf.data.Dataset.from_tensor_slices(dataset).batch(64, drop_remainder=True)

generator.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
x_train, x_test, y_train, y_test = train_test_split(images, masks, test_size=0.1, random_state=42)
history = generator.fit(x_train, y_train, epochs=50, validation_split=0.1, batch_size=64)

fit(data, 10)

y_test = y_test.astype(bool)
y_pred_thresholded = y_pred_thresholded.astype(bool)

# Calculate confusion matrix and metrics
cm = confusion_matrix(y_test.flatten(), y_pred_thresholded.flatten())
f1 = f1_score(y_test.flatten(), y_pred_thresholded.flatten())
precision = precision_score(y_test.flatten(), y_pred_thresholded.flatten())
recall = recall_score(y_test.flatten(), y_pred_thresholded.flatten())
accuracy = accuracy_score(y_test.flatten(), y_pred_thresholded.flatten())

print("confusion_matrix:", cm)
print("f1_score:",f1)
print("precision:",precision)
print("recall",recall)
print("accuracy:",accuracy)

generator.save('/content/drive/MyDrive/modl.h5')

def calculate_iou(y_true, y_pred):
    intersection = np.logical_and(y_true, y_pred)
    union = np.logical_or(y_true, y_pred)
    iou_score = np.sum(intersection) / np.sum(union)
    return iou_score
def show_predictions(num_samples):
    total_iou=0
    for i in range(num_samples):
        idx = np.random.randint(images.shape[0])
        image, mask = images[idx], masks[idx]
        predicted = generator.predict(tf.expand_dims(image, axis=0))[0]
        predicted_binary = (predicted > 0.5).astype(np.uint8)

        iou = calculate_iou(mask, predicted_binary)
        total_iou += iou


        plt.figure(figsize=(10,8))

        plt.subplot(1,3,1)
        plt.imshow(image)
        plt.title("Satellite Image " + str(i + 1))
        plt.axis('off')

        plt.subplot(1,3,2)
        plt.imshow(mask)
        plt.title("Map Image " + str(i + 1))
        plt.axis('off')

        plt.subplot(1,3,3)
        plt.imshow(predicted)
        plt.title("Predicted Image " + str(i + 1))
        plt.axis('off')

        plt.show()
    mean_iou = total_iou / num_samples
    print("Mean IoU:", mean_iou)

show_predictions(10)