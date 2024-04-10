from datetime import date
from src.database.models import Contact, User
from src.schemas import ContactModel
from sqlalchemy.orm import Session
from sqlalchemy import extract, and_


async def get_contacts(limit: int, offset: int, user: User, db: Session):
    contacts = db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_email(email: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_phone(phone: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.phone == phone, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_first_name(first_name: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.first_name == first_name, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_second_name(second_name: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.second_name == second_name, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_birth_date(birth_date: date, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.birth_date == birth_date, Contact.user_id == user.id)).first()
    return contact


async def create(body: ContactModel, current_user: User, db: Session):
    contact = Contact(**body.dict(), user=current_user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body: ContactModel, user: User, db: Session):
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
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts_birthday(start_date: date, end_date: date, db: Session):
    birth_day = extract('day', Contact.birth_date)
    birth_month = extract('month', Contact.birth_date)
    contacts = db.query(Contact).filter(
        birth_month == extract('month', start_date),
        birth_day.between(extract('day', start_date), extract('day', end_date))
    ).all()
    return contacts
