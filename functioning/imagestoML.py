#run in terminal first
# pip install tensorflow keras numpy matplotlib opencv-python
#python version used 3.11.6 - https://www.python.org/downloads/release/python-3116/


import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Input, Lambda
from tensorflow.keras.models import Model
import numpy as np
import cv2
import os
import random 
import matplotlib.pyplot as plt

# Load and preprocess images
def load_image(image_path, target_size=(128, 128)):
    print(f"Loading image from path: {image_path}")  # Print the file path
    
    # Check if the file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File does not exist at path: {image_path}")
    
    # Check if the file is accessible
    if not os.access(image_path, os.R_OK):
        raise PermissionError(f"File is not accessible at path: {image_path}")
    
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    
    img = cv2.resize(img, target_size)
    img = img.astype("float32") / 255.0  # Normalize
    return img

# Load dataset with image pairs (same subject vs. different subject)
def load_dataset(image_dir, num_pairs=1000):
    image_files = os.listdir(image_dir)
    image_paths = [os.path.join(image_dir, f) for f in image_files]
    
    pairs = []
    labels = []
    
    for _ in range(num_pairs):
        # Positive pair (same subject)
        img1_path = random.choice(image_paths)
        img2_path = random.choice(image_paths)  # Could be improved with subject-based filtering
        pairs.append((load_image(img1_path), load_image(img2_path)))
        labels.append(1)

        # Negative pair (different subject)
        img3_path = random.choice(image_paths)
        img4_path = random.choice(image_paths)
        while img3_path == img4_path:  # Ensure different images
            img4_path = random.choice(image_paths)
        pairs.append((load_image(img3_path), load_image(img4_path)))
        labels.append(0)
    
    return np.array(pairs), np.array(labels)

# Define the Siamese Network
def build_siamese_network(input_shape=(128, 128, 3)):
    input_layer = Input(shape=input_shape)
    
    x = Conv2D(64, (3, 3), activation="relu", padding="same")(input_layer)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    
    x = Conv2D(128, (3, 3), activation="relu", padding="same")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    
    x = Conv2D(256, (3, 3), activation="relu", padding="same")(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    
    x = Flatten()(x)
    x = Dense(512, activation="relu")(x)
    
    model = Model(inputs=input_layer, outputs=x)
    return model

# Create the Siamese Model
def build_siamese_model(input_shape):
    base_network = build_siamese_network(input_shape)
    
    input_a = Input(shape=input_shape)
    input_b = Input(shape=input_shape)
    
    processed_a = base_network(input_a)
    processed_b = base_network(input_b)
    
    # Calculate L1 distance between the two feature vectors
    l1_distance = Lambda(lambda tensors: tf.abs(tensors[0] - tensors[1]))([processed_a, processed_b])
    
    # Final prediction layer
    output = Dense(1, activation="sigmoid")(l1_distance)
    
    model = Model(inputs=[input_a, input_b], outputs=output)
    return model

# Train the model
def train_siamese_model(image_dir, batch_size=32, epochs=10):
    pairs, labels = load_dataset(image_dir, num_pairs=2000)
    
    # Separate images into two inputs
    x1 = np.array([pair[0] for pair in pairs])
    x2 = np.array([pair[1] for pair in pairs])
    
    # Build model
    model = build_siamese_model(input_shape=(128, 128, 3))
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    
    # Train the model
    model.fit([x1, x2], labels, batch_size=batch_size, epochs=epochs, validation_split=0.2)
    
    return model

# Test the model on new image pairs
def predict_similarity(model, img1_path, img2_path):
    img1 = load_image(img1_path)
    img2 = load_image(img2_path)
    
    img1 = np.expand_dims(img1, axis=0)
    img2 = np.expand_dims(img2, axis=0)
    
    similarity_score = model.predict([img1, img2])[0][0]
    return similarity_score

# Example usage:
# model = train_siamese_model("path/to/your/image/dataset")
# score = predict_similarity(model, "image1.jpg", "image2.jpg")
# print(f"Similarity Score: {score:.2f}")
model = train_siamese_model(r"C:\Users\herop\OneDrive\Documents\!College\!BBraunFiles\imagesML\22_Gauge_XYZ_Clockwise_Rotations")
print("Model trained successfully.")
print("Predicting similarity score for the following images:")
print(r"C:\Users\herop\OneDrive\Documents\!College\!BBraunFiles\imagesML\22_Gauge_XYZ_Clockwise_Rotations\22_Gauge_BaseCase.png")
print(r"C:\Users\herop\OneDrive\Documents\!College\!BBraunFiles\imagesML\22_Gauge_XYZ_Clockwise_Rotations\22_Gauge_XYZ_Clockwise_Rotations-0044.png")
score = predict_similarity(model, r"C:\Users\herop\OneDrive\Documents\!College\!BBraunFiles\imagesML\22_Gauge_XYZ_Clockwise_Rotations\22_Gauge_BaseCase.png", r"C:\Users\herop\OneDrive\Documents\!College\!BBraunFiles\imagesML\22_Gauge_XYZ_Clockwise_Rotations\22_Gauge_XYZ_Clockwise_Rotations-0044.png")
print(f"Similarity Score: {score:.2f}")