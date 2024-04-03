import os
import cv2
import numpy as np
import json

# Load face dataset
dataset_dir = "Dataset"
faces = []
labels = []
folder_names = []  # To store folder names

label_dict = {}  # Dictionary to map folder names to integers
current_label = 0

for root, dirs, files in os.walk(dataset_dir):
    for dir_name in dirs:
        folder_names.append(dir_name)  # Store folder names
        label_dict[dir_name] = current_label
        current_label += 1
        subdir_path = os.path.join(dataset_dir, dir_name)
        for file in os.listdir(subdir_path):
            if file.endswith("jpg") or file.endswith("png"):
                img_path = os.path.join(subdir_path, file)
                label = label_dict[dir_name]
                img = cv2.imread(img_path, 0)
                faces.append(img)
                labels.append(label)

# Train recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(labels))

# Save trained model
recognizer.save("trained_model.yml")

# Store metadata (folder names) in a JSON file
with open("metadata.json", "w") as f:
    json.dump(folder_names, f)
