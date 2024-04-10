from datetime import datetime, date

from pydantic import BaseModel, EmailStr, Field


class ContactModel(BaseModel):
    first_name: str
    second_name: str
    email: EmailStr
    phone: str
    birth_date: date
    user_id: int = Field(1, gt=0)
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    class Config:
        orm_mode = True


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    second_name: str
    email: EmailStr
    phone: str
    birth_date: date
    created_at: datetime
    updated_at: datetime
    user: UserResponse

    class Config:
        orm_mode = True


class ContactCreateUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: datetime
    additional_data: str = None


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=50)
    email: EmailStr


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
