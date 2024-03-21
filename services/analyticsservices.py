from models import UserTicket
from services.dbservices import db_dependency as db

# event_id = 1
# event_no = db.query(UserTicket).filter(UserTicket.event_id==event_id).all()

# r=0
# if event_no.ticket_type == 'regular':
#     r+=1

# def count(value: list):
#     r = 0
#     for i in value:
#         if value.ticket_type == 'regular':
#             r+=1
#         elif value.ticket_type == 'plus 2':
#             r+=2
#         elif value.ticket_type == 'plus 3':
#             r+=3
#         elif value.ticket_type == 'plus 4':
#             r+=4
            
#         return r

             


def counter(Value: list):
    r = 0
    for i in Value:
        r+=1
    return r

def counterp1(Value: list):
    r = 0
    for i in Value:
        r+=2
    return r

def counterp2(Value: list):
    r = 0
    for i in Value:
        r+=3
    return r

def counterp3(Value: list):
    r = 0
    for i in Value:
        r+=4
    return r

def counterp4(Value: list):
    r = 0
    for i in Value:
        r+=5
    return r