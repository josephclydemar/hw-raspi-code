import cv2 as cv # type: ignore


def identify_face(HAAR_CASCADE, FACE_RECOGNIZER, frame, known_users):
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces_rect = HAAR_CASCADE.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
    for x, y, w, h in faces_rect:
        faces_roi = gray_frame[y:y+h, x:x+w]
        label, confidence = FACE_RECOGNIZER.predict(faces_roi)
        cv.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), thickness=1)
        if confidence > 50:
            cv.putText(frame, f'P: {known_users[label]}   C: {confidence:.2f}%', (x - 10, y - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), thickness=2)
        else:
            cv.putText(frame, 'P: unknown', (x - 10, y - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), thickness=2)