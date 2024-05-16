import cv2 # type: ignore

def rescale_frame(frame, scale=0.75):
    return cv2.resize(frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale)), interpolation=cv2.INTER_AREA)

