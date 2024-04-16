import configparser
import pathlib

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from src.conf.config import settings

URI = settings.sqlalchemy_database_url

engine = create_engine(URI, echo=True)
DBSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """
The get_db function is a context manager that will automatically close the database session at the end of a request.
It also handles any exceptions that occur during the request, and aborts with an HTTP 400 error if one occurs.

:return: A database connection, which is used by all the functions that need to query the database
:doc-author: Trelent
"""
    db = DBSession()
    try:
        yield db
    except SQLAlchemyError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()
