from fastapi import APIRouter, status, HTTPException, Depends
from models import UserTicket, EventTicket, Event
from services.dbservices import db_dependency
from services.analyticsservices import counter, counterp1, counterp2, counterp3, counterp4
from routes.user_auth import user_dependency
from sqlalchemy import func
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter



# total number of ticket
# tot num of ticket aquired
# tot num of ticket clocked_in



lytics = APIRouter()

# Endpoint to see how many tickets we are available
@lytics.get("/ticket_avalabile/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache()
async def number_ticket_assigned(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event = db.query(EventTicket).filter(EventTicket.event_id==event_id).first()
    return event.ticket_available
    

# Endpoint to see how many regular tickets have been bought
@lytics.get("/ticks_regs/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def regular_ticket_bought(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event_no = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='regular').all()
    ticket_holders = counter(event_no)
    return ticket_holders


# Endpoint to see how many Plus one tickets have been bought
@lytics.get("/ticks_one/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def plus_one_ticket_bought(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event_no = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus one').all()
    ticket_holders = counterp1(event_no)
    return ticket_holders


# Endpoint to see how many plus 2 tickets have been bought
@lytics.get("/ticks_two/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def  plus_2_ticket_bought(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event_no = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus two').all()
    ticket_holders = counterp2(event_no)
    return ticket_holders


# Endpoint to see how many plus 3 tickets have been bought
@lytics.get("/ticks_three/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def plus_3_ticket_bought(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event_no = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus three').all()
    ticket_holders = counterp3(event_no)
    return ticket_holders


# Endpoint to see how many Plus 4 tickets have been bought
@lytics.get("/ticks_four/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def plus_4_ticket_bought(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event_no = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus four').all()
    ticket_holders = counterp4(event_no)
    return ticket_holders



# Endpoint to see how many total tickets have been bought
@lytics.get("/ticks_tots/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def total_ticket_bought(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event_no_1 = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='regular').all()
    holders_1 = counter(event_no_1)

    event_no_2 = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus one').all()
    holders_2 = counterp1(event_no_2)

    event_no_3 = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus two').all()
    holders_3 = counterp2(event_no_3)

    event_no_4 = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus three').all()
    holders_4 = counterp3(event_no_4)

    event_no_5 = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_type=='plus four').all()
    holders_5 = counterp4(event_no_5)

    ticket_holders = holders_1 + holders_2 + holders_3 + holders_4 + holders_5
    return ticket_holders



# Endpoint to see how many ticket are left
@lytics.get("/ticket_remaining/{event_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def number_ticket_left(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    total = db.query(EventTicket).filter(EventTicket.event_id==event_id).first()
    event_no = db.query(UserTicket).filter(UserTicket.event_id==event_id)
    acquired = counter(event_no)
    grand = int(total.ticket_available) - int(acquired)
    return grand


# Endpoint to see how many attendees to an event at the time
@lytics.get("/attendees", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=120)
async def number_attendees(event_id: int, user: user_dependency, db: db_dependency):
    if user.get("role")!="Eventor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    event_list = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.clocked==True).all()
    attendees_value = counter(event_list)
    return attendees_value
   
