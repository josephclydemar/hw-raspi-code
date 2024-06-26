import os
from PIL import Image # type: ignore
from keras.models import load_model # type: ignore
from keras_facenet import FaceNet # type: ignore
import numpy as np # type: ignore
import pickle # type: ignore
import cv2 # type: ignore

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_net = FaceNet()

# Directory containing folders of images for each person
folder = 'faces_with_night_vision'

# Initialize database dictionary
database = {}

# Function to extract embeddings from images
def extract_embeddings(image_path):
    # Read image from file
    gbr1 = cv2.imread(image_path)
    
    # Detect face
    haar = face_cascade.detectMultiScale(gbr1, 1.1, 4)
    
    if len(haar) > 0:
        x1, y1, width, height = haar[0]
    else:
        return None  # Skip images without faces
    
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    
    # Convert image to RGB and resize for FaceNet
    gbr = cv2.cvtColor(gbr1, cv2.COLOR_BGR2RGB)
    gbr = Image.fromarray(gbr)
    gbr_array = np.asarray(gbr)
    face = gbr_array[y1:y2, x1:x2]
    face = Image.fromarray(face)
    face = face.resize((160, 160))
    face = np.asarray(face)
    
    # Expand dimensions for FaceNet input
    face = np.expand_dims(face, axis=0)
    
    # Get FaceNet embedding
    signature = face_net.embeddings(face)
    
    return signature

# Traverse through each folder in 'faces_with_night_vision/' and use folder names as labels
for person_folder in os.listdir(folder):
    person_path = os.path.join(folder, person_folder)
    if os.path.isdir(person_path):
        print(f'Processing images for {person_folder}')
        
        # Initialize lists to store embeddings and weights for the person
        embeddings = []
        weights = []
        
        # Traverse through images in the person's folder
        for filename in os.listdir(person_path):
            image_path = os.path.join(person_path, filename)
            
            # Extract embedding from image if face is detected
            signature = extract_embeddings(image_path)
            if signature is not None:
                embeddings.append(signature)
                weights.append(1.0)  # Default weight for each embedding
        
        # Calculate weighted average embedding for the person
        if embeddings:
            weighted_avg_embedding = np.average(embeddings, axis=0, weights=weights)
            
            # Add person's weighted average embedding to the database
            database[person_folder] = weighted_avg_embedding

print('Embeddings extraction completed.')

myfile = open(os.path.join('trained_models', 'data3.pkl'), 'wb')
pickle.dump(database, myfile)
myfile.close()