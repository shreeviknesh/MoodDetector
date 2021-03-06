# Local Imports
from .CollectData import return_faces
from .CONSTANTS import *

# Library Imports
import os
import cv2
import numpy as np
from sklearn.preprocessing import normalize
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

def detect_faces(image, model):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 6)

    if len(faces) != 0:
        x, y, w, h = faces[0]
        face_image = gray[y:y+h, x:x+w]

        resized_image = cv2.resize(face_image, IMAGE_SIZE, interpolation=cv2.INTER_CUBIC).reshape(1, IMAGE_SIZE[0] * IMAGE_SIZE[1])
        resized_image = normalize(resized_image).reshape(1, IMAGE_SIZE[0], IMAGE_SIZE[1], 1)

        mood_index = np.argmax(model.predict(resized_image))

        color = (255, 0, 0)
        if mood_index == 1:
            color = (0, 0, 255)

        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, f"{MOODS[mood_index]}", (50, 100), font, 0.75, color, 2)

    cv2.imshow('Image', image)

def detect():
    try:
        model = tf.keras.models.load_model(os.path.join(os.path.abspath(MODEL_FOLDER), "model.h5"))
    except:
        print("[Error] Model not found. Train your model first.")
        exit(0)

    print("[Info] Press Spacebar to exit")
    capture = cv2.VideoCapture(0)
    while True:
        check, frame = capture.read()
        frame = cv2.flip(frame, 1)

        detect_faces(frame, model)

        key = cv2.waitKey(1)

        if key == ord(' '):
            exit(0)

    capture.release()
    cv2.destroyAllWindows()