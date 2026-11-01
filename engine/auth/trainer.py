import os
import cv2
import numpy as np
from PIL import Image

base_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base_dir, 'samples')
cascade_path = os.path.join(base_dir, "haarcascade_frontalface_default.xml")
trainer_dir = os.path.join(base_dir, 'trainer')
os.makedirs(trainer_dir, exist_ok=True)
model_path = os.path.join(trainer_dir, 'trainer.yml')

if not hasattr(cv2, 'face'):
    print("[Error] cv2.face module is not available. Please install opencv-contrib-python to train LBPH models.")
    exit(1)

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cascade_path)

def Images_And_Labels(sample_folder):
    if not os.path.exists(sample_folder):
        return [], []
    imagePaths = [os.path.join(sample_folder, f) for f in os.listdir(sample_folder) if f.endswith('.jpg') or f.endswith('.png')]     
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        gray_img = Image.open(imagePath).convert('L')
        img_arr = np.array(gray_img, 'uint8')

        try:
            face_id = int(os.path.split(imagePath)[-1].split(".")[1])
        except (IndexError, ValueError):
            continue

        faces = detector.detectMultiScale(img_arr)
        for (x, y, w, h) in faces:
            faceSamples.append(img_arr[y:y+h, x:x+w])
            ids.append(face_id)

    return faceSamples, ids

print("Training faces. It will take a few seconds. Wait...")
faces, ids = Images_And_Labels(path)

if len(faces) == 0:
    print("No face samples found in:", path)
else:
    recognizer.train(faces, np.array(ids))
    recognizer.write(model_path)
    print(f"Model trained successfully on {len(faces)} samples and saved to: {model_path}")