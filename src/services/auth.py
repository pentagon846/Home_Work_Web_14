from datetime import datetime, timedelta
from typing import Optional

import redis
import pickle
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)  # ..

    def verify_password(self, plain_password, hashed_password):
        """
    The verify_password function takes a plain-text password and hashed
    password as arguments. It then uses the pwd_context object to verify that the
    plain-text password matches the hashed one.

    :param self: Make the method a bound method, which means that it can be called on objects of this class
    :param plain_password: Pass in the password that the user enters when they log in
    :param hashed_password: Compare the plain_password parameter to see if they match
    :return: A boolean value
    :doc-author: Trelent
    """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
    The get_password_hash function takes a password as input and returns the hash of that password.
    The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

    :param self: Represent the instance of the class
    :param password: str: Pass the password to be hashed into the function
    :return: A string that is the hash of the password
    :doc-author: Trelent
    """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):

        """
    The create_access_token function creates a new access token for the user.
        Args:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[float]): The time in seconds until the token expires. Defaults to 15 minutes if not specified.

    :param self: Refer to the class itself
    :param data: dict: Pass in the data that will be encoded into the token
    :param expires_delta: Optional[float]: Set the expiration time of the access token
    :return: A string
    :doc-author: Trelent
    """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

    :param self: Represent the instance of the class
    :param data: dict: Pass in the data that will be encoded into the token
    :param expires_delta: Optional[float]: Set the expiry time of the refresh token
    :return: A refresh token that is encoded with the user's id, username, and email
    :doc-author: Trelent
    """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
    The get_current_user function is a dependency that will be used in the
        protected endpoints. It takes a token as an argument and returns the user
        if it's valid, otherwise raises an HTTPException with status code 401.

    :param self: Access the class attributes
    :param token: str: Get the token from the request header
    :param db: Session: Get the database session
    :return: The user object
    :doc-author: Trelent
    """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        if user is None:
            raise credentials_exception
        return user

    async def decode_refresh_token(self, refresh_token: str):
        """
    The decode_refresh_token function is used to decode the refresh token.
    It takes a refresh_token as an argument and returns the email of the user if it's valid.
    If not, it raises an HTTPException with status code 401 (UNAUTHORIZED) and detail 'Could not validate credentials'.


    :param self: Represent the instance of the class
    :param refresh_token: str: Pass in the refresh token that was sent to the client
    :return: The email of the user who is trying to refresh their access token
    :doc-author: Trelent
    """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def create_email_token(self, data: dict):
        """
    The create_email_token function takes a dictionary of data and returns a token.
    The token is encoded with the SECRET_KEY, which is stored in the .env file.
    The algorithm used to encode the token is also stored in the .env file.

    :param self: Represent the instance of the class
    :param data: dict: Pass in the user's email address
    :return: A token
    :doc-author: Trelent
    """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=3)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str):
        """
    The get_email_from_token function takes a token as an argument and returns the email associated with that token.
    If the scope of the token is not 'email_token', then it raises an HTTPException. If there is a JWTError,
    it also raises an HTTPException.

    :param self: Represent the instance of the class
    :param token: str: Pass in the token that is sent to the user's email
    :return: The email that was passed in the payload of the jwt token
    :doc-author: Trelent
    """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'email_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope to token')
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Invalid token for email verification')


auth_service = Auth()
