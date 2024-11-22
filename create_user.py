import face_recognition
import cv2
import numpy as np
import requests
import json

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(2)

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = 0

resize_coef = 1

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame == 9:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=resize_coef, fy=resize_coef)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.array(small_frame[:, :, ::-1])

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for index, face_encoding in enumerate(face_encodings):
            name = f'User[{index}]'

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
<<<<<<< HEAD
            "password": password,
            "embeddings": face_encodings[index]
        })
        response = requests.post('http://localhost:8000/api/create', data=data, headers=headers)
        if response.status_code == 201:
            print(f'User {username} was successfully found in database')
            print(f'Embeddings was successfully added to database')
=======
            "password": password
        })
        response = requests.post('http://localhost:8000/api/create', data=data, headers=headers)
        if response.status_code == 201:
            users = requests.post('http://127.0.0.1:8000/api/list?offset=0&limit=100').json()
            for user in users:
                if user["username"] == username:
                    id = user["id"]
                    print(f'User {username} was successfully found in database')
                    break
            else:
                print('Some troubles')
>>>>>>> 423826a21ce6ef2feb6ac4de6c9c7e6c9d8a75a9
        else:
            print(f'User {username} was not added to database')
            print(str(response.text))

<<<<<<< HEAD
=======
        data = json.dumps({
            "id": id,
            "username": username,
            "embeddings": face_encodings[index].tolist()
        })
        response = requests.put('http://localhost:8000/api/update', data=data, headers=headers)
        if response.status_code == 204:
            print(f'Embeddings was successfully added to database')
        else:
            print(f'Embeddings was not added to database')
            print(str(response.text))

>>>>>>> 423826a21ce6ef2feb6ac4de6c9c7e6c9d8a75a9
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()