from datetime import date
from src.database.models import ContactModel, User
from src.schemas import ContactModel
from sqlalchemy.orm import Session
from sqlalchemy import extract, and_


async def get_contacts(limit: int, offset: int, user: User, db: Session):
    """
The get_contacts function returns a list of contacts for the user.

:param limit: int: Limit the number of contacts returned
:param offset: int: Skip a certain number of contacts
:param user: User: Get the user id from the database
:param db: Session: Access the database
:return: A list of contacts
:doc-author: Trelent
"""
    contacts = db.query(ContactModel).filter(ContactModel.user_id == user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    """
The get_contact_by_id function takes in a contact_id and user, and returns the contact with that id.
    Args:
        contact_id (int): The id of the desired Contact object.
        user (User): The User object associated with this request.

:param contact_id: int: Specify the id of the contact that is being retrieved
:param user: User: Get the user id from the user object
:param db: Session: Pass a database session to the function
:return: The contact with the given id
:doc-author: Trelent
"""
    contact = db.query(ContactModel).filter(and_(ContactModel.id == contact_id, ContactModel.user_id == user.id)).first()
    return contact


async def get_contact_by_email(email: str, user: User, db: Session):
    """
The get_contact_by_email function takes in an email and a user, and returns the contact with that email.
    Args:
        email (str): The contact's unique identifier.
        user (User): The current logged-in user.

:param email: str: Pass in the email of the contact we want to find
:param user: User: Identify the user that is making the request
:param db: Session: Pass the database session to the function
:return: The contact with the given email and user
:doc-author: Trelent
"""
    contact = db.query(ContactModel).filter(and_(ContactModel.email == email, ContactModel.user_id == user.id)).first()
    return contact


async def get_contact_by_phone(phone: str, user: User, db: Session):
    """
The get_contact_by_phone function takes in a phone number and user object,
and returns the contact associated with that phone number.


:param phone: str: Get the phone number of a contact
:param user: User: Filter the contacts by user
:param db: Session: Access the database
:return: A contact object
:doc-author: Trelent
"""
    contact = db.query(ContactModel).filter(and_(ContactModel.phone == phone, ContactModel.user_id == user.id)).first()
    return contact


async def get_contact_by_first_name(first_name: str, user: User, db: Session):
    """
The get_contact_by_first_name function takes in a first_name and user object, and returns the contact with that
first name. If no such contact exists, it returns None.

:param first_name: str: Filter the database for contacts with a matching first name
:param user: User: Identify the user who is making the request
:param db: Session: Pass the database session to the function
:return: A contact object
:doc-author: Trelent
"""
    contact = db.query(ContactModel).filter(and_(ContactModel.first_name == first_name, ContactModel.user_id == user.id)).first()
    return contact


async def get_contact_by_second_name(second_name: str, user: User, db: Session):
    """
The get_contact_by_second_name function returns a contact by second name.

:param second_name: str: Filter the contacts by second name
:param user: User: Get the user's id from the database
:param db: Session: Access the database
:return: The first contact with the specified second name
:doc-author: Trelent
"""
    contact = db.query(ContactModel).filter(and_(ContactModel.second_name == second_name, ContactModel.user_id == user.id)).first()
    return contact


async def get_contact_by_birth_date(birth_date: date, user: User, db: Session):
    """
The get_contact_by_birth_date function returns a contact object from the database based on the birth_date parameter.
    The function takes in three parameters:
        - birth_date: A date object representing the birthday of a contact.
        - user: A User object representing an authenticated user. This is used to ensure that only contacts belonging to this user are returned by this function.
        - db: An SQLAlchemy Session instance, which is used for querying and updating data in our database.

:param birth_date: date: Filter the contacts by birth date
:param user: User: Get the user_id from the user object
:param db: Session: Pass a database session to the function
:return: The contact with the specified birth date and user id
:doc-author: Trelent
"""
    contact = db.query(ContactModel).filter(and_(ContactModel.birth_date == birth_date, ContactModel.user_id == user.id)).first()
    return contact


async def create(body: ContactModel, current_user: User, db: Session):
    """
The create function creates a new contact in the database.


:param body: ContactModel: Get the data from the request body
:param current_user: User: Check if the user is authenticated
:param db: Session: Pass the database session to the function
:return: The contact model
:doc-author: Trelent
"""
    contact = ContactModel(**body.dict(), user=current_user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body: ContactModel, user: User, db: Session):
    """
The update function updates a contact in the database.
    Args:
        contact_id (int): The id of the contact to update.
        body (ContactModel): The updated information for the specified user.

:param contact_id: int: Identify the contact to be deleted
:param body: ContactModel: Pass the data from the request body to the function
:param user: User: Get the user_id from the token
:param db: Session: Access the database
:return: The updated contact
:doc-author: Trelent
"""
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        contact.first_name = body.first_name
        contact.second_name = body.second_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birth_date = body.birth_date
        db.commit()
    return contact


async def remove(contact_id: int, user: User, db: Session):
    """
The remove function removes a contact from the database.
    Args:
        contact_id (int): The id of the contact to be removed.
        user (User): The user who is removing the contact.
        db (Session): A connection to our database, used for querying and updating data.

:param contact_id: int: Specify the id of the contact to be removed
:param user: User: Check if the user is logged in
:param db: Session: Pass the database session to the function
:return: The contact that was removed, if it exists
:doc-author: Trelent
"""
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts_birthday(start_date: date, end_date: date, db: Session):
    """
The get_contacts_birthday function returns a list of contacts whose birthdays fall between the start_date and end_date.
The function takes in three parameters:
    - start_date: The first date to check for birthdays (inclusive)
    - end_date: The last date to check for birthdays (inclusive)
    - db: A database session object that is used to query the database.  This parameter is automatically passed by FastAPI when you use dependency injection.

:param start_date: date: Set the start date of the range
:param end_date: date: Set the end date of the range
:param db: Session: Pass the database session to the function
:return: A list of contacts whose birthdays are between the start date and end date
:doc-author: Trelent
"""
    birth_day = extract('day', ContactModel.birth_date)
    birth_month = extract('month', ContactModel.birth_date)
    contacts = db.query(ContactModel).filter(
        birth_month == extract('month', start_date),
        birth_day.between(extract('day', start_date), extract('day', end_date))
    ).all()
    return contacts
