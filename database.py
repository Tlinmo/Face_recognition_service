import requests
import json
import numpy as np

def add_user_to_db(username, password, embeddings):
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    data = json.dumps({
        "username": username,
        "password": password,
        "embedding": embeddings
    })
    response = requests.post('http://localhost:8000/api/auth/create', data=data, headers=headers)
    return response

def put_user_to_db(id, username, embeddings):
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    data = json.dumps({
        "username": username,
        "embedding": embeddings
    })
    response = requests.put(f'http://localhost:8000/api/users/{id}', data=data, headers=headers)
    return response

def get_users(offset=0, limit=100):
    response = requests.get(f'http://localhost:8000/api/users/?offset={offset}&limit={limit}')
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
                "embeddings": [np.array(embedding) for embedding in item["embedding"]]
            })
    return users

