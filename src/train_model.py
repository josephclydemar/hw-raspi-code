import os
import numpy as np # type: ignore
import cv2 as cv # type: ignore






def train_face_recognizer(train_dir: str, val_dir: str, people):
    features = []
    labels = []
    if os.path.exists('model_trained.yml'):
        os.remove('model_trained.yml')
        print('---- Overwriting Old Trained Model ----')
    else:
        print('------ Saving a New Trained Model ------')

    for person in people:
        path = os.path.join(train_dir, person)
        label = people.index(person)

        for img in os.listdir(path):
            img_path = os.path.join(path, img)
            img_array = cv.imread(img_path)
            gray_img_array = cv.cvtColor(img_array, cv.COLOR_BGR2GRAY)
            features.append(gray_img_array)
            labels.append(label)
    
    features = np.array(features, dtype='object')
    labels = np.array(labels)

    # face_recognizer = cv.face.LBPHFaceRecognizer_create()
    face_recognizer = cv.face.LBPHFaceRecognizer.create()
    face_recognizer.train(features, labels)

    # np.save('./parameters/features.npy', features)
    # np.save('./parameters/labels.npy', labels)

    face_recognizer.save('model_trained.yml')
    print('*****************************************  Training Finished  *****************************************')




if __name__ == '__main__':
    train_face_recognizer()




