from typing import List

from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/auth", tags=['auth'])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def signup(body: UserModel, background_task: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
The signup function creates a new user in the database.
    It takes in a UserModel object, which is validated by pydantic.
    The password is hashed using Argon2 and stored as such.


:param body: UserModel: Get the user information from the request body
:param background_task: BackgroundTasks: Add a task to the background tasks queue
:param request: Request: Get the base url of the request
:param db: Session: Get the database session
:return: The newly created user, but it also sends an email to the new user
:doc-author: Trelent
"""
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_task.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
The login function is used to authenticate a user.
    It takes the username and password from the request body,
    verifies them against the database, and returns an access token if successful.

:param body: OAuth2PasswordRequestForm: Get the username and password from the request body
:param db: Session: Get the database session
:return: A dictionary with the access_token, refresh_token and token type
:doc-author: Trelent
"""
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email is not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
The refresh_token function is used to refresh the access token.
    The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
    If the user's current refresh_token does not match what was passed into this function then it will return an error.

:param credentials: HTTPAuthorizationCredentials: Get the token from the request header
:param db: Session: Create a database session
:return: A new access_token and refresh_token
:doc-author: Trelent
"""
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
The confirmed_email function is used to confirm a user's email address.
    It takes the token from the URL and uses it to get the user's email address.
    Then, it checks if that user exists in our database. If not, we return an error message saying so.
    If they do exist, we check if their account has already been confirmed or not (if they've already clicked on this link).
    If their account has been confirmed, we return a message saying so; otherwise, we update their record in our database
    by setting &quot;confirmed&quot; to True and then return another success message.

:param token: str: Get the token from the url
:param db: Session: Get the database session
:return: A message that the email is already confirmed or a message that the email was confirmed
:doc-author: Trelent
"""
    email = auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email was confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_task: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
The request_email function is used to send an email to the user with a link that will confirm their account.
    The function takes in a RequestEmail object, which contains the user's email address. It then checks if there
    is already an account associated with that email address and whether or not it has been confirmed yet. If it
    hasn't been confirmed, we add a task to our background_task queue (which was passed into this function) using
    FastAPI's BackgroundTasks class and call our send_email() function from utils/mailer.py.

:param body: RequestEmail: Get the email from the request body
:param background_task: BackgroundTasks: Add a task to the background tasks queue
:param request: Request: Get the base_url of the server
:param db: Session: Get the database session
:return: A message to the user, but it also adds a task to the background_task object
:doc-author: Trelent
"""
    user = await repository_users.get_user_by_email(body.email, db)
    if user and user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_task.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation"}
