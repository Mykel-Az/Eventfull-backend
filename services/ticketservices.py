# from schemas.ticketschemas import TicketType
import qrcode
import qrcode.image.svg
from fastapi import UploadFile, File, HTTPException, status
import shutil
import os
import cv2
from pyzbar.pyzbar import decode
import time 
from models import UserTicket, EventTicket
from services.dbservices import db_dependency


qr = qrcode.QRCode(version = 4, box_size = 10, border = 1)
UPLOAD_DIRECTORY = "qrcode_files"

def ticket_qr_code(eventee_name:str, ticket_code:str, ticket_type: str):
    content = ticket_code
    qr.add_data(content)
    qr.make(fit = True)
    qrcode_img = qr.make_image(fill_color = 'black', back_color = 'white')
    save_as = f"{ticket_code}.png"
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIRECTORY, save_as)
    qrcode_img.save(save_path)
    return save_as






def qrcode_Scanner(db: db_dependency, event_id: int):
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    used_codes = []

    camera = True
    while camera == True:
        success, frame = cap.read()

        for code in decode(frame):
            data = code.data.decode('utf-8')
            if data is not None: 
                info = db.query(UserTicket).filter(UserTicket.event_id==event_id).filter(UserTicket.ticket_code==data[2]).first() 
                time.sleep(5)
                return info
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ticket probably doesn't exist")

        cv2.imshow('Testing-code-scan', frame)
        cv2.waitKey(3)




# def ticket_avalability(type:TicketType, no_of_ticket:int):
#     if type == TicketType.regular:
#         tick_no = no_of_ticket - 1
#     elif type == TicketType.plus_one:
#         tick_no = no_of_ticket - 2
#     elif type == TicketType.plus_two:
#         tick_no = no_of_ticket - 3
#     elif type == TicketType.plus_three:
#         tick_no = no_of_ticket -4
#     elif type == TicketType.plus_four:
#         tick_no = no_of_ticket - 5

#     return tick_no


def code_innit(event: str):
    k = event.split(" ")
    if len(k) > 1:
        r = []
        for words in k:
            r.append(words[0])
            p = "".join(r)
        return p.lower()
    else:
        return event[0:2]
    

# p = [1,2,3,4,5,6,7,8,9,9,0]
# r = 0
# for i in p:
#     r+=1
#     print(r)




