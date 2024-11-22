import cv2

from InsightFaceRecognition import MyFaceAnalysis
from database import add_user_to_db, get_users, parse_users, put_user_to_db

# Запускаем модель распознавания лица
app = MyFaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640,640))

# Получаем доступ к камере
cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("Ошибка доступа к веб-камере")
    exit(-1)

faces = []
process_this_frame = 7

while True:
    # Считываем изображение с камеры
    ret, frame = cap.read()

    # Каждый 8 кадр считываем лица
    if process_this_frame == 7:
        faces = app.detect(frame)
        app.recognize(frame, faces)
        for index, face in enumerate(faces):
            face.name = f'User[{index}]'
            face.known = False
        process_this_frame = 0
    process_this_frame += 1

    # Рисуем края лиц и выводим картинку
    cv2.imshow('Video', app.draw_on(frame, faces))

    # Выходим из программы, если нажали 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('й'):
        break
    if key == ord('c') or key == ord('с'): # Добавляем человека в базу, если нажали 'c'
        username = input('Введите Фамилию и Имя: ')
        password = input('Введите пароль для входа: ')
        index = int(input('Введите индекс человека на камере, которого вы хотите добавить в базу: '))

        response = add_user_to_db(username, password, [faces[index].embedding.tolist()])
        if response.status_code == 201:
            print(f'{username} успешно добавлен в базу данных')
        elif response.status_code == 409:
            users = parse_users(get_users())
            for user in users:
                if user["username"] == username:
                    print(f'{username} был успешно найден в базе данных')

                    response = put_user_to_db(user["id"], user["username"], [faces[index].embedding.tolist()])
                    if response.status_code == 204:
                        print(f'Данные лица были успешно обновлены в базе данных')
                    else:
                        print(f'Не удалось обновить данные лица')
                        print(str(response.text))
                    break
            else:
                print('Some troubles')
        else:
            print(f'Не получилось добавить "{username}" в базу данных')
            print(str(response.text))

# Закрываем доступ к камере и окна
cap.release()
cv2.destroyAllWindows()
