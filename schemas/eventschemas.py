from fastapi import UploadFile
from models import Event
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional


class EventBase(BaseModel):
    title: str
    description: str
    country: str
    state: str
    city: str
    venue: str
    schedule: datetime
    more_description: str



class Section(str, Enum):
    none = "..."
    Sporting_Events = "Sporting_Events"
    Festivals = "Festivals"
    Corporate_Events = "Corporate_Events"
    Concerts = "Concerts"
    Private_Events = "Private_Events"
    Others = "Others"


class EventEdit(BaseModel):
    title: str
    city: str
    more_description: str
    venue: str
    schedule: datetime   


class Response(BaseModel):
    message: Optional [str] = None
    data : Optional [str | list | dict] = None