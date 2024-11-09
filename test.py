from insightface.app import FaceAnalysis
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import requests

# Инициализация приложения для анализа лиц InsightFace
app = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0, det_size=(256,256))

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Ошибка доступа к веб-камере")
    exit(-1)

usernames = []
embeddings = []
def get_users():
    global usernames, embeddings
    users = requests.get('http://127.0.0.1:8000/api/users?offset=0&limit=100').json()
    usernames = [item["username"] for item in users]
    embeddings = [np.array(item["embedding"][0]) for item in users]

def compare_embeddings_cos(embs, emb2):
    dists = []
    for emb in embs:
        dists.append(np.dot(emb, emb2) / (np.linalg.norm(emb) * np.linalg.norm(emb2)))

    index = np.argmin(dists)
    return dists[index], index

def compare_embeddings_euq(embs, emb2):
    dists = []
    for emb in embs:
        dists.append(np.linalg.norm(np.array(emb / np.linalg.norm(emb) - emb2 / np.linalg.norm(emb2))))

    index = np.argmin(dists)
    return dists[index], index

# Пороговое значение для сравнения лиц (можно подбирать экспериментально)
THRESHOLD = 1.2
face_locations = []
face_encodings = []
face_names = []
face_similarities = []
faces = []
process_this_frame = 14

resize_coef = 0.5

while True:
    # Grab a single frame of video
    ret, frame = cap.read()

    # Only process every other frame of video to save time
    if process_this_frame == 14:
        get_users()
        face_locations = []
        face_encodings = []
        face_similarities = []
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=resize_coef, fy=resize_coef)

        # Find all the faces and face encodings in the current frame of video
        faces = app.get(small_frame)

        face_names = []
        for index, face in enumerate(faces):
            dist, index = compare_embeddings_euq(embeddings, face.embedding)
            if dist <= THRESHOLD:
                name = f'{usernames[index]} {float(int(dist * 100)) / 100}'
            else:
                name = f'Неизвестный {float(int(dist * 100)) / 100}'

            face_names.append(name)
            face_similarities.append(dist)
            face_locations.append(face.bbox)
            face_encodings.append(face.embedding)
            for i in range(4):
                face.bbox[i] *= int(1 / resize_coef)
            for i in range(5):
                face.kps[i][0] *= int(1 / resize_coef)
                face.kps[i][1] *= int(1 / resize_coef)

        process_this_frame = 0

    process_this_frame += 1

    frame = app.draw_on(frame, faces)
    # Display the results
    for (left, top, right, bottom), name, dist in zip(face_locations, face_names, face_similarities):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top = int(top)
        right = int(right)
        bottom = int(bottom)
        left = int(left)

        # Draw a box around the face
        if dist > THRESHOLD:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        image_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(image_pil)
        text_x, text_y = left + 6, bottom - 32
        draw.text((text_x, text_y), name, font=font, fill=(255, 255, 255))
        frame = np.array(image_pil)

    # Display the resulting image
    cv2.imshow('Video', frame)

    key = cv2.waitKey(1) & 0xFF
    # Hit 'q' on the keyboard to quit!
    if key == ord('q') or key == ord('й'):
        break

# Release handle to the webcam
cap.release()
cv2.destroyAllWindows()  