import cv2

from InsightFaceRecognition import MyFaceAnalysis
from database import compare_face
from translate_text import transliterate

import time

# Запускаем модель распознавания лица
app = MyFaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640,640))

# Получаем доступ к камере
cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("Ошибка доступа к веб-камере")
    exit(-1)

process_this_frame = 7

while True:
    # Считываем изображение с камеры
    ret, frame = cap.read()

    # Каждый 15 кадр считываем лица
    if process_this_frame == 7:
        start_time = time.perf_counter()
        # Ищем лица на камере
        faces = app.detect(frame)
        mid_time = time.perf_counter()
        # Получаем черты лиц
        app.recognize(frame, faces)
        end_time = time.perf_counter()

        face_names = []
        for _, face in enumerate(faces):
            response = compare_face(face.embedding.tolist())
            if response is not None:
                face.name = response["username"] + " " + str(response["embeddings"][0]["similarity"])
                cv2.imshow(transliterate(response["username"]), face.img)
                face.known = True
            else:
                face.name = 'Неизвестный'
                face.known = False
        process_this_frame = 0
    process_this_frame += 1

    # Рисуем края лиц и выводим картинку
    cv2.imshow('Video', app.draw_on(frame, faces, f'{(mid_time - start_time):.6f}', f'{(end_time - mid_time):.6f}'))

    # Выходим из программы, если нажали 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('й'):
        break

# Закрываем доступ к камере и окна
cap.release()
cv2.destroyAllWindows()
