# Local Imports
from .CONSTANTS import FACE_CASCADE, TRAINING_FOLDER, TRAIN_SIZE_PER_MOOD, IMAGE_SIZE, MOODS

# Library Imports
import cv2
import os
import shutil
import pickle
import numpy as np
from sklearn.preprocessing import normalize

def return_faces(image, show=True, return_all=False):
    # Grayscale image because color doesn't factor into the mood of the person in the pic
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Default parameters as per docs
    faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 6)

    # Creates a list of all faces detected in the frame
    face_images = []
    for (x, y, w, h) in faces:
        face_images.append(gray[y:y+h, x:x+w])

    try:
        # Only considering the first face in all the faces
        # If training phase considers more than one face per frame
        # Change the code with a for loop
        if show:
            cv2.imshow('Frame', face_images[0])

        if return_all:
            # Resizing all the images to a standard size
            all_faces = []
            for face in face_images:
                resized_image = cv2.resize(face, IMAGE_SIZE, interpolation=cv2.INTER_CUBIC)
                all_faces.append(resized_image)
            return all_faces

        else:
            resized_image = cv2.resize(face_images[0], IMAGE_SIZE, interpolation=cv2.INTER_CUBIC)
            return resized_image

    except:
        # IF face_images is empty, i.e., no faces are detected in the frame
        return None

def capture_video(mood):
    capture = cv2.VideoCapture(0)

    frame_count = 1
    while frame_count <= TRAIN_SIZE_PER_MOOD:
        check, frame = capture.read()
        frame = cv2.flip(frame, 1)

        frame_face = return_faces(frame)
        key = cv2.waitKey(1)

        # This makes sure that every frame has a valid face in it
        # And that we don't save empty images to the training folder
        if frame_face is not None:
            cv2.imwrite(
                f'{TRAINING_FOLDER}/{mood}/{frame_count}.jpg', frame_face)
            print('[Info] Image saved')
            frame_count += 1

        else:
            print('[Error] None')

        if key == ord(' '):
            break

    capture.release()
    cv2.destroyAllWindows()

def create_folders():
    # Removing the pre-existing training data, if any
    # And creating the required folders & sub-folders
    if os.path.exists(TRAINING_FOLDER):
        shutil.rmtree(TRAINING_FOLDER)

    # Creating the empty folder
    os.mkdir(TRAINING_FOLDER)

    # Creating a sub-folder in training_folder for each mood
    for mood in MOODS:
        os.mkdir(os.path.join(TRAINING_FOLDER, mood))

def convert_images_to_array():
    """
        A function to convert the captured & stored JPEG images into a numpy array.

        This allows us to directly use the images without having to process them everytime
        we train a model.
    """

    def read_image(file_path):
        """An inner function that just returns the image as a numpy array from the given file path."""
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        return img

    training_images = []
    training_labels = []
    for i, mood in enumerate(MOODS):
        path = os.path.join(os.path.abspath(TRAINING_FOLDER), mood)
        images = [os.path.join(path, filename) for filename in os.listdir(path)]

        count = len(images)
        mood_data = []

        for file_path in images:
            image = read_image(file_path).reshape(IMAGE_SIZE[0] * IMAGE_SIZE[1])  # * IMAGE_SIZE[2] if channels is included
            mood_data.append(image)

        training_images = training_images + mood_data

        # Adding the same label for each image for this mood
        training_labels = training_labels + ([i] * count)

    # Normalizing the images from the range 0-255
    training_images = normalize(training_images)

    # Reshaping the data to fit the requirements of CNNs
    training_images = np.array(training_images).reshape(len(training_images), IMAGE_SIZE[0], IMAGE_SIZE[1], 1)
    training_labels = np.array(training_labels).reshape(len(training_images))

    training_data_file_path = os.path.join(os.path.abspath(TRAINING_FOLDER), 'training_data.pickle')

    with open(training_data_file_path, 'wb') as file:
        pickle.dump({
            'x': training_images,
            'y': training_labels
        }, file)

    return (training_images.shape, training_labels.shape)

def collect_training_data():
    # Making all lower case to make sure there's no issues with naming
    for i in range(len(MOODS)):
        MOODS[i] = MOODS[i].lower()

    create_folders()

    # Getting training data for all the moods
    for mood in MOODS:
        img = np.zeros((256, 512, 1), np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, f'make {mood} faces', (100, 128), font, 1, (255, 255, 255), 2)
        cv2.imshow("Mood", img)
        cv2.waitKey(1000)
        # cv2.destroyAllWindows()

        capture_video(mood)

    convert_images_to_array()