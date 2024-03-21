from fastapi import APIRouter, status, HTTPException, Path, UploadFile, File, Form, Depends
from schemas.eventschemas import EventBase, Section, EventEdit, Response
from models import Event, User
from services.dbservices import db_dependency
from services.Eventservices import save_to_file, UPLOAD_DIRECTORY
from routes.user_auth import user_dependency
from typing import Optional, List, Annotated
from starlette.responses import FileResponse
import os
import requests
import requests_cache 
import uuid
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter


vent = APIRouter()


# EVENTOR PREVILEDGES

# Endpoint to create an Event
@vent.post("/create", status_code=status.HTTP_201_CREATED)
async def create_Event(user: user_dependency, db: db_dependency, request: EventBase, catergory: Section):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
    person =  db.query(User).filter(User.id==user.get('id')).first()
    event_model = Event(
        title = request.title,
        description = request.description,
        country = request.country,
        state = request.state,
        city = request.city,
        venue = request.venue,
        more_description = request.more_description,
        schedule = request.schedule,
        catergory = catergory,
        organizer = person.full_name,
        owner_id = user.get("id")
    )

    db.add(event_model)
    db.commit()

    return {"Message": "Event successfully created"}


# Endpoint to uplaod the event theme
@vent.put("/event_theme/{event_id}")
async def upload_theme(user: user_dependency, db: db_dependency, event_id: int, canvas: UploadFile = File()):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event = db.query(Event).filter(Event.id==event_id).first()

    file = save_to_file(canvas, UPLOAD_DIRECTORY)
    event.theme = file

    db.add(event)
    db.commit()
    return 


# Endpoint to return the event theme
@vent.get("/event_theme/{event_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_theme(user: user_dependency, db: db_dependency, event_id: int):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    event = db.query(Event).filter(Event.id==event_id).first()
    filename = event.theme
    return FileResponse(os.path.join(UPLOAD_DIRECTORY, filename))


# Endpoint to delete the event theme
@vent.delete("/event_theme/{event_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_theme(user: user_dependency, db: db_dependency, event_id: int):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    event = db.query(Event).filter(Event.id==event_id).first()
    db.delete(event.theme)
    db.commit()
    return {"message": "theme delete"}


# requests_cache.install_cache("Event", backend="sqlite")


# Endpoint for the eventor to see all event created  
@vent.get("/display", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def display_eventor_events(user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event_list = db.query(Event).filter(Event.owner_id == user.get("id")).all()
    if event_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return event_list


# Endpoint to view an Event and share Link
@vent.get("/view/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=500)
async def view_event(event_id: str, user: user_dependency, db: db_dependency):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Generate unique sharable link to view the event (localhost)
    event_link = f"http://localhost:8000/events/{event_id}"  # Assuming your FastAPI server runs on port 8000
    
    theme = FileResponse(os.path.join(UPLOAD_DIRECTORY, event.theme))

    return {
        "canvas": theme,
        "details": event,
        "event_link": event_link
    }



# Endpoint to edit an Event
@vent.put("/edit/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def edit_event(event_id: int, user: user_dependency, db: db_dependency, request: EventEdit):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event = db.query(Event).filter(Event.id==event_id).filter(Event.owner_id==user.get("id")).first()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    event.title = request.title
    event.city = request.city
    event.more_description = request.more_description
    event.venue = request.venue
    event.schedule = request.schedule

    db.add(event)
    db.commit()

    return {
        "Title": event.title,
        "Description": event.description,
        "Organizer": event.organizer,
        "date": event.schedule,
        "edited": True
    }


# Endpoint to Delete a Event
@vent.delete("/delete/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_event(event_id:str, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event = db.query(Event).filter(Event.id==event_id).filter(Event.owner_id==user.get("id")).first()

    db.delete(event)
    db.commit()

    return Response(message="Event deleted Successfully")




# EVENTEE PREVILEGDES

# Endpoint to see all events created
@vent.get("/display_all", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def display_all_event(user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event_list = db.query(Event).all()
    return event_list


# EVENT FILTERS

# Endpoint to see events by categories
@vent.get("/filter_by/{category}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=180)
async def categories_filter(category: Section, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event_list = db.query(Event).filter(Event.catergory==category).all()
    if event_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Event as been created under this category")
    
    return event_list


# Endpoint to see event by country state
@vent.get("/filter/{country}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=180)
async def country_filter(country: str, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventee":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    event_list = db.query(Event).filter(Event.country==country).all()
    if event_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Event as been created in this country")

    return event_list


# # Endpoint
# Endpoint to see event by state
# @vent.get("/filter/{state}", status_code=status.HTTP_200_OK)
# @cache(expire=180)
# async def state_filter(state: str, user: user_dependency, db: db_dependency):
#     if user.get("role")!="Eventee":
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
#     event_list = db.query(Event).filter(Event.state==state).all()
#     if event_list is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Event as been created in this country")
    
#     return event_list


# Endpoint to see event by organizer
# @vent.get("/filter/{organizer}", status_code=status.HTTP_200_OK)
# @cache(expire=180)
# async def organizer_filter(organizer: str, user: user_dependency, db: db_dependency):
#     if user.get("role")!="Eventee":
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
#     event_list = db.query(Event).filter(Event.organizer==organizer).all()
#     if event_list is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Event as been created in this country")
    
#     return event_list




