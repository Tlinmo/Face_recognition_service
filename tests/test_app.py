import io
import pytest

import schemathesis
from hypothesis import HealthCheck, settings
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from app.settings import settings as stgs
from app.settings import APP_ROOT

schema = schemathesis.from_uri(f"{stgs.base_url}/api/openapi.json")

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.large_base_example])
@schema.parametrize()
async def test_api(case, auth_token):
    case.headers = case.headers or {}
    case.headers["Authorization"] = f"Bearer {auth_token}"
    
    case.call_and_validate()

@pytest.mark.anyio
async def test_upload_fake_image(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Test upload incorrect image file

    Args:
        client (AsyncClient): client for the app
        fastapi_app (FastAPI): current FastAPI application
    """
    image_data = io.BytesIO(b"fake image data")
    image_data.name = "test_image.png"

    url = fastapi_app.url_path_for("image_to_embedding")

    response = await client.post(url, files={"file": ("test_image.png", image_data, "image/png")})

    # Проверяем статус-код и содержимое ответа
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    

@pytest.mark.anyio
async def test_upload_real_image(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Test upload correct image file

    Args:
        client (AsyncClient): client for the app
        fastapi_app (FastAPI): current FastAPI application
    """
    image_path = APP_ROOT / "tests/recognution/Shimon_Peres_0003.jpg"
    assert image_path.exists(), "Image file does not exist."

    url = fastapi_app.url_path_for("image_to_embedding")
    
    with open(image_path, "rb") as image_file:
        response = await client.post(url, files={"file": ("test_image.jpg", image_file, "image/jpeg")})
    
    # Проверяем статус-код
    assert response.status_code == status.HTTP_200_OK
    
    # Проверяем что embedding есть
    assert "embedding" in response.json()[0]
    
    # Проверяем что вектор 512-мерный
    assert len(response.json()[0]["embedding"]) == 512
    

@pytest.mark.anyio
async def test_upload_real_image_and_create_user(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Test upload correct image file and create user

    Args:
        client (AsyncClient): client for the app
        fastapi_app (FastAPI): current FastAPI application
    """
    image_path = APP_ROOT / "tests/recognution/Shimon_Peres_0003.jpg"
    assert image_path.exists(), "Image file does not exist."

    url = fastapi_app.url_path_for("image_to_embedding")
    
    with open(image_path, "rb") as image_file:
        response = await client.post(url, files={"file": ("test_image.jpg", image_file, "image/jpeg")})
    
    # Проверяем статус-код
    assert response.status_code == status.HTTP_200_OK
    
    # Проверяем что embedding есть
    assert "embedding" in response.json()[0]
    
    # Проверяем что вектор 512-мерный
    assert len(response.json()[0]["embedding"]) == 512
    
    user_embedding = response.json()[0]["embedding"]
    url = fastapi_app.url_path_for("register")

    response = await client.post(url, json={"username": "ShimonPeres", "password": "test", "embeddings": [user_embedding]})
    
    assert response.status_code == status.HTTP_201_CREATED

# Что это за безобразие? Может тут лучше сделать через фикстуры? Будущий я явно с этим разберется
@pytest.mark.anyio
async def test_upload_real_image_and_create_user_and_search_user(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Test upload correct image file, create user, and search user

    Args:
        client (AsyncClient): client for the app
        fastapi_app (FastAPI): current FastAPI application
    """
    image_path = APP_ROOT / "tests/recognution/Shimon_Peres_0005.jpg"
    assert image_path.exists(), "Image file does not exist."

    url = fastapi_app.url_path_for("image_to_embedding")
    
    with open(image_path, "rb") as image_file:
        response = await client.post(url, files={"file": ("test_image.jpg", image_file, "image/jpeg")})
    
    assert response.status_code == status.HTTP_200_OK
    
    # Проверяем что embedding есть
    assert "embedding" in response.json()[0]
    
    # Проверяем что вектор 512-мерный
    assert len(response.json()[0]["embedding"]) == 512
    
    user_embedding = response.json()[0]["embedding"]
    
    url = fastapi_app.url_path_for("register")

    response = await client.post(url, json={"username": "ShimonPeres", "password": "test", "embeddings": [user_embedding]})
    
    assert response.status_code == status.HTTP_201_CREATED
    
    url = fastapi_app.url_path_for("face_embeddings_authentication")

    response = await client.post(url, json={"embedding": user_embedding})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "ShimonPeres"
