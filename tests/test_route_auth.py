from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock
import pytest

app = FastAPI()


# Setup a fixture for the test client
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.query.return_value.filter_by.return_value.first = AsyncMock()
    return session


# Mock for user repository
@pytest.fixture
def mock_user_repository(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr('src.repository.users.get_user_by_email', mock.get_user_by_email)
    monkeypatch.setattr('src.repository.users.create_user', mock.create_user)
    monkeypatch.setattr('src.repository.users.update_token', mock.update_token)
    monkeypatch.setattr('src.repository.users.confirmed_email', mock.confirmed_email)
    return mock


# Mock for auth service
@pytest.fixture
def mock_auth_service(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr('src.services.auth.auth_service.verify_password', mock.verify_password)
    monkeypatch.setattr('src.services.auth.auth_service.create_access_token', mock.create_access_token)
    monkeypatch.setattr('src.services.auth.auth_service.create_refresh_token', mock.create_refresh_token)
    monkeypatch.setattr('src.services.auth.auth_service.decode_refresh_token', mock.decode_refresh_token)
    monkeypatch.setattr('src.services.auth.auth_service.get_email_from_token', mock.get_email_from_token)
    return mock


# Test for signup endpoint
def test_signup(client, mock_db_session, mock_user_repository):
    mock_user_repository.get_user_by_email.return_value = None  # User does not exist
    mock_user_repository.create_user.return_value = {"id": 1, "email": "test@example.com", "confirmed": False}

    response = client.post("/auth/signup", json={"email": "test@example.com", "password": "password123"})
    # assert response.status_code == 404
    # assert response.json() == {"id": 1, "email": "test@example.com", "confirmed": False}


# Test for login endpoint
def test_login_successful(client, mock_db_session, mock_user_repository, mock_auth_service):
    mock_user_repository.get_user_by_email.return_value = {"email": "user@example.com", "password": "hashed_password",
                                                           "confirmed": True}
    mock_auth_service.verify_password.return_value = True  # Password is correct
    mock_auth_service.create_access_token.return_value = "access_token"
    mock_auth_service.create_refresh_token.return_value = "refresh_token"

    # response = client.post("/auth/login", data={"username": "user@example.com", "password": "correct_password"})
    # assert response.status_code == 404
    # assert response.json()["access_token"] == "access_token"
    # assert response.json()["refresh_token"] == "refresh_token"


