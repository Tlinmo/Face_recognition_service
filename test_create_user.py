from insightface.app import FaceAnalysis
import cv2
import requests
import json

# Инициализация приложения для анализа лиц InsightFace
app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(256,256))

cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("Ошибка доступа к веб-камере")
    exit(-1)

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
faces = []
process_this_frame = 7

resize_coef = 1

while True:
    # Grab a single frame of video
    ret, frame = cap.read()

    # Only process every other frame of video to save time
    if process_this_frame == 7:
        face_locations = []
        face_encodings = []
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=resize_coef, fy=resize_coef)

        # Find all the faces and face encodings in the current frame of video
        faces = app.get(small_frame)

        face_names = []
        for index, face in enumerate(faces):
            name = f'User[{index}]'

            face_names.append(name)
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
    for (left, top, right, bottom), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top = int(top)
        right = int(right)
        bottom = int(bottom)
        left = int(left)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    key = cv2.waitKey(1) & 0xFF
    # Hit 'q' on the keyboard to quit!
    if key == ord('q') or key == ord('й'):
        break

    # Hit 'c' on the keyboard to add user!
    if key == ord('c') or key == ord('с'):
        username = input('Enter your username: ')
        password = input('Enter your password: ')
        index = int(input('Enter index of user on image you want to add to database: '))

        # Creating user
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        data = json.dumps({
            "username": username,
            "password": password,
            "embedding": [face_encodings[index].tolist()]
        })
        response = requests.post('http://localhost:8000/api/auth/create', data=data, headers=headers)
        if response.status_code == 201:
            print(f'User {username} was successfully added to database')
        elif response.status_code == 409:
            users = requests.get('http://localhost:8000/api/users/?offset=0&limit=100').json()
            for user in users:
                if user["username"] == username:
                    id = user["id"]
                    print(f'User {username} was successfully found in database')

                    data = json.dumps({
                        "username": username,
                        "embedding": [face_encodings[index].tolist()]
                    })
                    response = requests.put(f'http://localhost:8000/api/users/{id}', data=data, headers=headers)
                    if response.status_code == 204:
                        print(f'Embedding was successfully added to database')
                    else:
                        print(f'Embedding was not added to database')
                        print(str(response.text))
                        
                    break
            else:
                print('Some troubles')
        else:
            print(f'User {username} was not added to database')
            print(str(response.text))

# Release handle to the webcam
cap.release()
cv2.destroyAllWindows()