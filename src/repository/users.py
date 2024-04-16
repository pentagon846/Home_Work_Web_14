from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
The get_user_by_email function takes in an email and a database session,
and returns the user with that email if it exists. If no such user exists,
it returns None.

:param email: str: Specify the email address of the user
:param db: Session: Pass the database session to the function
:return: A single user by email
:doc-author: Trelent
"""
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    """
The create_user function creates a new user in the database.
    Args:
        body (UserModel): The UserModel object to be created.
        db (Session): The SQLAlchemy session object used for querying the database.

:param body: UserModel: Pass the data from the request body to the function
:param db: Session: Create a database session
:return: A new user object, which is then passed to the response
:doc-author: Trelent
"""
    grav = Gravatar(body.email)
    new_user = User(**body.dict(), avatar=grav.get_image())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
The update_token function updates the refresh token for a user in the database.
    Args:
        user (User): The User object to update.
        refresh_token (str): The new refresh token to store in the database.
        db (Session): A connection to our Postgres database.

:param user: User: Get the user's id from the database
:param refresh_token: Update the user's refresh token in the database
:param db: Session: Pass the database session to the function
:return: Nothing
:doc-author: Trelent
"""
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
The confirmed_email function takes in an email and a database session,
and sets the confirmed field of the user with that email to True.


:param email: str: Get the user's email
:param db: Session: Pass the database connection to the function
:return: None
:doc-author: Trelent
"""
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
The update_avatar function updates the avatar of a user.

:param email: Find the user in the database
:param url: str: Specify the type of parameter that is being passed into the function
:param db: Session: Pass the database session to the function
:return: A user object
:doc-author: Trelent
"""
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
