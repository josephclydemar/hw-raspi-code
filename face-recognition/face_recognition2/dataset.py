import cv2
import os

# Initialize camera
cap = cv2.VideoCapture(0)

# Load face cascade
face_cascade = cv2.CascadeClassifier("model/haarcascade_frontalface_default.xml")

# Counter for capturing images
count = 0

# Input user's name
name = input("Enter your name: ")

# Create a directory for the user's dataset
user_dataset_dir = os.path.join("Dataset", name)
if not os.path.exists(user_dataset_dir):
    os.makedirs(user_dataset_dir)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Save the captured face
        cv2.imwrite(f"{user_dataset_dir}/{count}.jpg", gray[y:y+h, x:x+w])
        count += 1

        # Display the image
        cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or count >= 100:  # Capture 50 images or press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
