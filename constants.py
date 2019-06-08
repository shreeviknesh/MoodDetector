import cv2

# Initializing some constants
MOODS = ['happy', 'sad']
TRAINING_FOLDER = 'training_data'
TRAIN_SIZE_PER_MOOD = 250
IMAGE_SIZE = (150, 150)

# One channel
INPUT_SHAPE = tuple(list(IMAGE_SIZE) + [1])
NUM_CLASSES = len(MOODS)
EPOCHS = 10

# A variable to flag if the data has been collected or not
DATA_COLLECTED = True

# The classifier that detects faces
FACE_CASCADE = cv2.CascadeClassifier(
    'vendor/haarcascade_frontalface_default.xml')
