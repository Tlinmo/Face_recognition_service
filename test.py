import cv2

from InsightFaceRecognition import MyFaceAnalysis
from database import parse_users, get_users
from translate_text import transliterate

# Запускаем модель распознавания лица
app = MyFaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640,640))

# Получаем доступ к камере
cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("Ошибка доступа к веб-камере")
    exit(-1)

THRESHOLD = 1.2
faces = []
process_this_frame = 14

while True:
    # Считываем изображение с камеры
    ret, frame = cap.read()

    # Каждый 15 кадр считываем лица
    if process_this_frame == 14:
        users = parse_users(get_users())
        usernames = [user["username"] for user in users]
        embeddings = [user["embeddings"][0] for user in users]

        # Ищем лица на камере
        faces = app.detect(frame)
        # Получаем черты лиц
        app.recognize(frame, faces)

        face_names = []
        for _, face in enumerate(faces):
            # Сравниваем лица с лицами в базе данных
            dist, index = app.compare_euq(embeddings, face.embedding)

            # Если схожесть больше порога - выводим, что он в базе
            if dist <= THRESHOLD:
                face.name = f'{usernames[index]} {float(int(dist * 100)) / 100}'
                cv2.imshow(transliterate(usernames[index]), face.img)
                face.known = True
            else:
                face.name = f'Неизвестный {float(int(dist * 100)) / 100}'
                face.known = False
        process_this_frame = 0
    process_this_frame += 1

    # Рисуем края лиц и выводим картинку
    cv2.imshow('Video', app.draw_on(frame, faces))

    # Выходим из программы, если нажали 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('й'):
        break

# Закрываем доступ к камере и окна
cap.release()
cv2.destroyAllWindows()
