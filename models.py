from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, DateTime, func
from sqlalchemy_utils import ScalarListType
from sqlalchemy.orm import relationship
from uuid import UUID
import datetime


class User(Base):
    __tablename__='user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_pasword = Column(String, nullable=False)
    gender = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    # is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    is_active = Column(Boolean, default=True)
    role = Column(String)

    # events = relationship("Event", back_populates="owners")
    # userticket = relationship("UserTicketing", back_populates="owners")


class Event(Base):
    __tablename__='event'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(30), nullable=False)
    description = Column(String(255), nullable=False)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    more_description = Column(String(255), nullable=False)
    venue = Column(String)
    schedule = Column(String, nullable=False)
    organizer = Column(String, ForeignKey("user.full_name"))
    catergory = Column(String(15))
    theme = Column(String, unique=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.datetime.now)

    # owners = relationship("User", back_populates="events")
    # tickets = relationship("EventTicketing", back_populates="events")


class EventTicket(Base):
    __tablename__= 'event_ticket'

    id = Column(Integer, primary_key=True, index=True)
    ticket_user = Column(String, ForeignKey("user.full_name"))
    event_name = Column(String, ForeignKey("event.title"))
    schedule = Column(String, ForeignKey("event.schedule"))
    ticket_available = Column(Integer, nullable=False)
    venue = Column(String, ForeignKey("event.venue"))
    theme = Column(String, ForeignKey("event.theme"))
    reminder = Column(String)
    # ticket_type = Column(ScalarListType())
    event_id = Column(Integer, ForeignKey("event.id"))
    created_at = Column(DateTime, default=datetime.datetime.now)

    # events = relationship("Event", back_populates="event_ticket")


class UserTicket(Base):
    __tablename__= 'userticket'

    id = Column(Integer, primary_key=True, index=True)
    ticket_name = Column(String, ForeignKey('user.full_name'))
    user_id = Column(Integer, ForeignKey("user.id"))
    ticket_code = Column(String, unique=True, nullable=False)
    ticket_id = Column(Integer, ForeignKey("event_ticket.id"))
    event_id = Column(Integer, ForeignKey("event.id"))
    event_name = Column(String, ForeignKey("event_ticket.event_name"))
    event_theme = Column(String, ForeignKey("event.theme"))
    remind = Column(String, ForeignKey("event_ticket.reminder"))
    qr_code = Column(String)
    ticket_type = Column(String, nullable=False)
    clocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # owners = relationship("User", back_populates="userticket")


class Analytics(Base):
    __tablename__= 'analytics'

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("event.id"))
    total_ticket = Column(Integer, ForeignKey('event_ticket.ticket_available'))
    ticket_acquired = Column(Integer)
    ticket_clocked = Column(Integer)
