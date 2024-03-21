from pydantic import BaseModel, EmailStr
from typing import Optional, Annotated
from fastapi import Form
from enum import Enum
from models import User

class EventRoles(str, Enum):
    none = "..."
    Eventor = "Eventor"
    Eventee = "Eventee"


class Gender(str, Enum):
    none = '...'
    Male = 'Male'
    Female = 'Female'
    Non_binary = 'Non-binary'
    Rather_not_say = 'Rather not say'    

class Role(str, Enum):
    Eventor = 'Eventor',
    Eventee = 'Eventee'



class UserBase(BaseModel):
    username: Annotated[str, Form()]
    full_name: Annotated[str, Form()]
    email: Annotated[EmailStr, Form()]
    password: Annotated[str, Form()]
    confirm_password: Annotated[str, Form()]


class UserProfile(BaseModel):
    country: Annotated[str, Form()]
    state: Annotated[str, Form()]
    city: Annotated[str, Form()]


class Token(BaseModel):
    access_token: str
    token_type: str


class Response(BaseModel):
    message: Optional [str] = None
    data : Optional [str | list | dict] = None