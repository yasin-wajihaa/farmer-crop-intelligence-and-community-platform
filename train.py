import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os
import json

# ---------------- PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(BASE_DIR, "data/plantvillage/color")

print("Dataset path:", DATASET)
print("TensorFlow version:", tf.__version__)

# ---------------- GPU (optional) ----------------
gpus = tf.config.list_physical_devices('GPU')
print("GPUs found:", gpus)

# ---------------- IMAGE SETTINGS ----------------
IMG_SIZE = 128
BATCH = 8

# ---------------- DATA GENERATOR ----------------
train_data = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=15,
    zoom_range=0.1,
    horizontal_flip=True
)

train = train_data.flow_from_directory(
    DATASET,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH,
    class_mode='categorical',
    subset='training'
)

val = train_data.flow_from_directory(
    DATASET,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH,
    class_mode='categorical',
    subset='validation'
)

print("Classes:", train.num_classes)

# ---------------- MODEL ----------------
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(128,128,3)),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(train.num_classes, activation='softmax')
])

model.summary()

# ---------------- COMPILE ----------------
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ---------------- TRAIN ----------------
history = model.fit(
    train,
    validation_data=val,
    epochs=10
)
with open("class_indices.json", "w") as f:
    json.dump(train.class_indices, f)

# ---------------- SAVE ----------------
model.save("model.keras")
print("Model saved successfull")
