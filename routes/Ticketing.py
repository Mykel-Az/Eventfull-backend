from fastapi import APIRouter, status, HTTPException, Path, UploadFile, File, Form, Query, Depends
from schemas.ticketschemas import Ticketbase, TicketType, Remind
from services.ticketservices import code_innit, ticket_qr_code, UPLOAD_DIRECTORY,  qrcode_Scanner
from models import Event, User, EventTicket, UserTicket
from services.dbservices import db_dependency
from routes.user_auth import user_dependency, Response
from services.analyticsservices import counter
from typing import Optional, List, Annotated
from starlette.responses import FileResponse, StreamingResponse
import os
from uuid import UUID
import cv2
from pyzbar.pyzbar import decode
import time 
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter


vent = APIRouter()


# Endpoint to create Ticket prototype
@vent.post("/create/", status_code=status.HTTP_201_CREATED)
async def ticket_prototype(event_id: int, user: user_dependency, db: db_dependency
                           , ticket_for_event: int, reminder: Remind, ticket_types: List[TicketType] = Query(...)):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    person = db.query(User).filter(User.id==user.get("id")).first()
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    ticket_model = EventTicket(
        event_id = event_id,
        ticket_user = person.full_name,
        theme = event.theme,
        event_name = event.title,
        schedule = event.schedule,
        ticket_available = ticket_for_event,
        venue = event.venue,
        reminder = reminder,
        ticket_type = ticket_types
    )

    db.add(ticket_model)
    db.commit()
    return ticket_model


# Endpoint to edit ticket prototype


# Endpoint for an eventee to acquire a ticket
@vent.post("/acquire/{event_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def acquire_tickets(event_id: int, user: user_dependency, db: db_dependency, tick: TicketType, reminder: Remind):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_det = db.query(User).filter(User.id==user.get('id')).first()
    ticket_list = db.query(UserTicket).filter(UserTicket.event_id==event_id)
    event_ticket = db.query(EventTicket).filter(EventTicket.event_id == event_id).first()
    if  event_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tickets for this Events are not yet available")
    brev = code_innit(event_ticket.event_name)
    ticket_model = UserTicket(
        ticket_name = user_det.full_name,
        event_id = event_ticket.event_id,
        ticket_id = event_ticket.id,
        event_name = event_ticket.event_name,
        event_theme = event_ticket.theme,
        ticket_code =  brev + str(UUID(int=counter(ticket_list) + 1)),
        user_id = user.get("id"),
        ticket_type = tick,
        remind = reminder
    )
    
    db.add(ticket_model)
    db.commit()
    return {'Message': f'Congratulations ticket acquired, your ticket code is {ticket_model.ticket_code}'}


# Endpoint to view your ticket
@vent.get('/view/{event_id}', dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=300)
async def view_ticket(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    ticket_list = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.user_id==user.get('id')).first()
    if ticket_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return ticket_list




# Endpoint to delete your ticket
@vent.delete('/delete/{event_id}', dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_ticket(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    ticket = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.user_id==user.get('id')).first()
    print(ticket)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    db.delete(ticket)
    db.commit()
    return ticket


# Endpoint to get qrcode of a ticket for an event
@vent.put("/Qr_code/{event_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def ticket_qrcode(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event_ticket = db.query(UserTicket).filter(UserTicket.event_id == event_id).filter(UserTicket.user_id==user.get('id')).first()
    if event_ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    code_name = ticket_qr_code(event_ticket.event_name, event_ticket.ticket_code, event_ticket.ticket_type)
    event_ticket.qr_code = code_name

    db.add(event_ticket)
    db.commit()    
    # return FileResponse(os.path.join(UPLOAD_DIRECTORY, code_name))
    return {"message": "Qr_code is ready. click on get qr_code to view"}


# # Endpoint to return the qr_code theme
@vent.get("/qrcode/{event_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=False)
async def get_qrcode(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    ticket = db.query(UserTicket).filter(UserTicket.event_id == event_id).filter(UserTicket.user_id==user.get('id')).first()
    filename = ticket.ticket_code + '.png'
    return FileResponse(os.path.join(UPLOAD_DIRECTORY, filename))


#  Endpoint for qr_code scanner
@vent.put("/Qr_Scanner/")
async def code_scanner(user: user_dependency, db: db_dependency, event_id: int):
    if user.get("role") != "Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    camera = True
    try:
        while camera:
            success, frame = cap.read()

            if not success:
                continue

            for code in decode(frame):
                qrdata = code.data.decode('utf-8')
                print(qrdata)
                if qrdata:
                    info = db.query(UserTicket).filter(UserTicket.event_id == event_id).filter(UserTicket.ticket_code == qrdata).first()
                    if info:
                        if info.clocked != True:
                            info.clocked = True
                            db.commit()
                            time.sleep(3)
                            return 'Approved',{
                                'Name': info.ticket_name,
                                'Ticket code': info.ticket_code,
                                'Ticket Type': info.ticket_type,
                            } 
                        return 'Already clocked in', info
                    else:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket probably doesn't exist")

            cv2.imshow('Testing-code-scan', frame)
            if cv2.waitKey(30) & 0xFF == 27:
                break  

    finally:
        cap.release()  
