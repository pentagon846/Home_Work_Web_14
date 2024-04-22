import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar


@pytest.fixture
def mock_db_session():
    # Create a mock database session
    session = MagicMock(spec=Session)
    session.query.return_value.filter_by.return_value.first = MagicMock()
    return session


@pytest.fixture
def mock_user():
    return User(id=1, email='user@example.com', confirmed=False)


@pytest.mark.asyncio
async def test_get_user_by_email_found(mock_db_session, mock_user):
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    user = await get_user_by_email('user@example.com', mock_db_session)
    assert user == mock_user
    mock_db_session.query.assert_called_with(User)


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(mock_db_session):
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    user = await get_user_by_email('nonexistent@example.com', mock_db_session)
    assert user is None


@pytest.mark.asyncio
async def test_create_user(mock_db_session):
    mock_user_model = UserModel(email='newuser@example.com', username='newuser', password='password12345')
    new_user = await create_user(mock_user_model, mock_db_session)
    assert new_user.email == 'newuser@example.com'
    assert mock_db_session.add.called
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_update_token(mock_db_session, mock_user):
    await update_token(mock_user, 'new_token', mock_db_session)
    assert mock_user.refresh_token == 'new_token'
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_confirmed_email(mock_db_session, mock_user):
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    await confirmed_email(mock_user.email, mock_db_session)
    assert mock_user.confirmed is True
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_update_avatar(mock_db_session, mock_user):
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user
    new_avatar_url = 'http://example.com/newavatar.jpg'
    updated_user = await update_avatar(mock_user.email, new_avatar_url, mock_db_session)
    assert updated_user.avatar == new_avatar_url
    assert mock_db_session.commit.called
