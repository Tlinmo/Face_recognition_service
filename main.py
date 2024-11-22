import face_recognition
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

video_capture = cv2.VideoCapture(2)

usernames = []
embeddingss = []
def get_users():
    global usernames, embeddingss
    users = requests.post('http://127.0.0.1:8000/api/list?offset=0&limit=100').json()
    usernames = [item["username"] for item in users]
    embeddingss = [np.array(item["embeddings"]) for item in users]

process_this_frame = 0
face_locations = []
face_names = []

resize_coef = 1

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame == 14:
        get_users()
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=resize_coef, fy=resize_coef)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.array(small_frame[:, :, ::-1])

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(embeddingss, face_encoding, 0.6)
            name = "Unknown"

            face_distances = face_recognition.face_distance(embeddingss, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = usernames[best_match_index] + f' {int(100 - face_distances[best_match_index] * 100)}%'
            else:
                name = f'Unknown {int(100 - face_distances[best_match_index] * 100)}%'

            face_names.append(name)

        process_this_frame = 0

    process_this_frame += 1

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= int(1 / resize_coef)
        right *= int(1 / resize_coef)
        bottom *= int(1 / resize_coef)
        left *= int(1 / resize_coef)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        image_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(image_pil)
        text_x, text_y = left + 6, bottom - 32
        draw.text((text_x, text_y), name, font=font, fill=(255, 255, 255))
        frame = np.array(image_pil)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()