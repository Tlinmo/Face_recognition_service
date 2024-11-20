import requests
import json
import numpy as np

host = "http://frserver.tlinmo.pro/"

def add_user_to_db(username, password, embeddings):
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    data = json.dumps({
        "username": username,
        "password": password,
        "embeddings": embeddings
    })
    response = requests.post(f'{host}api/auth/create', data=data, headers=headers)
    return response

def put_user_to_db(id, username, embeddings):
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    data = json.dumps({
        "username": username,
        "embeddings": embeddings
    })
    response = requests.put(f'{host}api/users/{id}', data=data, headers=headers)
    return response


def compare_face(embedding):
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    data = json.dumps({
        "embedding": embedding
    })
    response = requests.post(f'{host}api/auth/face', data=data, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None





def get_users(offset=0, limit=100):
    response = requests.get(f'{host}api/users/?offset={offset}&limit={limit}')
    if response.status_code == 200:
        return response.json()
    else:
        return None

def parse_users(users_data):
    users = []
    for item in users_data:
        users.append(
            {
                "id": item["id"],
                "username": item["username"],
                "embeddings": [np.array(embedding) for embedding in item["embeddings"]]
            })
    return users

