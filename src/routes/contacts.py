from datetime import date, timedelta, datetime
from typing import List

from fastapi import Depends, HTTPException, Path, status, APIRouter, Query
from sqlalchemy import extract
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Contact
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel, ContactResponse, ContactCreateUpdate
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=['contacts'])





@router.post("/contacts/", response_model=ContactResponse)
def create_contact(
        contact: ContactCreateUpdate,
        db: Session = Depends(get_db),
        current_user: Contact = Depends(auth_service.get_current_user)
):
    """
The create_contact function creates a new contact in the database.

:param contact: ContactCreateUpdate: Pass in the contact information
:param db: Session: Access the database
:param current_user: Contact: Get the current user from the database
:return: A contactresponse object
:doc-author: Trelent
"""
    db_contact = Contact(**contact.dict(), user_id=current_user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return ContactResponse(**db_contact.__dict__)


@router.get("/upcoming_birthdays/", response_model=List[ContactResponse])
def upcoming_birthdays(db: Session = Depends(get_db)):
    """
The upcoming_birthdays function returns a list of contacts with birthdays in the next week.

:param db: Session: Access the database
:return: A list of contactresponse objects
:doc-author: Trelent
"""
    today = datetime.now().date()
    next_week = today + timedelta(days=7)

    contacts = []

    for single_day in (today + timedelta(days=n) for n in range(8)):
        day_contacts = db.query(Contact).filter(
            extract('month', Contact.birthday) == single_day.month,
            extract('day', Contact.birthday) == single_day.day
        ).all()
        contacts.extend(day_contacts)

    unique_contacts = list(set(contacts))

    return [ContactResponse(**contact.__dict__) for contact in unique_contacts]


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: Contact = Depends(auth_service.get_current_user)
):
    """
The get_contact function returns a ContactResponse object, which is the same as a Contact model.
The function takes in an integer contact_id and uses it to query the database for that specific contact.
If no such contact exists, then an HTTPException is raised with status code 404 (Not Found).
Otherwise, if the user does exist in the database, then their information will be returned.

:param contact_id: int: Specify the id of the contact to be retrieved
:param db: Session: Get the database session
:param current_user: Contact: Get the current user
:return: A contactresponse object, which is the same as a contact object but without the user_id attribute
:doc-author: Trelent
"""
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactResponse(**contact.__dict__)


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
        contact_id: int,
        contact: ContactCreateUpdate,
        db: Session = Depends(get_db),
        current_user: Contact = Depends(auth_service.get_current_user)
):
    """
The update_contact function updates a contact in the database.
    It takes an id, a ContactCreateUpdate object, and optionally a db Session and current_user.
    If no user is provided it will use the auth_service to get one from the Authorization header of the request.
    The function then queries for that contact in our database using its id and user_id (to ensure only contacts belonging to that user are updated).
    If no such contact exists we raise an HTTPException with status code 404 (Not Found) and detail &quot;Contact not found&quot;.

:param contact_id: int: Identify the contact to be updated
:param contact: ContactCreateUpdate: Pass the contact data to update
:param db: Session: Get the database session
:param current_user: Contact: Get the current user from the database
:return: A contactresponse object
:doc-author: Trelent
"""
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return ContactResponse(**db_contact.__dict__)


@router.delete("/contacts/{contact_id}", response_model=ContactResponse)
def delete_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: Contact = Depends(auth_service.get_current_user)
):
    """
The delete_contact function deletes a contact from the database.

:param contact_id: int: Specify the id of the contact that will be deleted
:param db: Session: Get a database session
:param current_user: Contact: Get the currently logged in user
:return: A contactresponse object
:doc-author: Trelent
"""
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return ContactResponse(**db_contact.__dict__)