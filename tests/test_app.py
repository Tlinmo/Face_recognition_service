import pytest

from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status
import schemathesis
from hypothesis import HealthCheck, settings

# Замените 'http://test' на URL вашего приложения
schema = schemathesis.from_uri("http://127.0.0.1:8000/api/openapi.json")

@pytest.fixture()
async def auth_token(client: AsyncClient, fastapi_app: FastAPI):
    """
    Фикстура для получения токена авторизации.
    """
    url = fastapi_app.url_path_for("authentication")
    response = await client.post(url, json={"username": "test", "password": "test"})
    response.raise_for_status()
    return response.json()["access_token"]


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@schema.parametrize()
async def test_api(case, auth_token):
    if not case.headers:
        case.headers = {}
        
    case.headers["Authorization"] = f"Bearer {auth_token}"
    response = case.call()
    case.validate_response(response)

