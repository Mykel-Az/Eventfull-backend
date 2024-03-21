# from fastapi import BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status, FastAPI, Request
# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
# from pydantic import BaseModel, EmailStr
# from starlette.responses import JSONResponse
# from typing import List
# from dotenv import dotenv_values
# from .models import User
# from services.authservices import create_access_token
# from starlette.templating import Jinja2Templates
# from datetime import timedelta
# import jwt
# from services.authservices import oauth2_bearer


# config_credentials = dotenv_values(".env")
# templates = Jinja2Templates(directory="templates")




# conf = ConnectionConfig(
#     MAIL_USERNAME= config_credentials["EMAIL"],
#     MAIL_PASSWORD= config_credentials["PASSWORD"],
#     MAIL_FROM= config_credentials["EMAIL"],
#     MAIL_PORT= 587,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_STARTTLS=True,
#     MAIL_SSL_TLS=False,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True,
# )


# class EmailSchema(BaseModel):
#     email: List[EmailStr]

# async def send_email(email: EmailSchema, instance: User, request: Request):
#     token_data = {'username' :instance.username, 'id': instance.id}

#     token = jwt.encode(token_data, config_credentials['SECRET'], oauth2_bearer)

#     template = templates.TemplateResponse("verify.html", {"request": request})

#     message = MessageSchema(
#         subject= "Eventful Account Verification",
#         recipients= email,
#         body= template,
#         subtype= MessageType.html
#     )

#     fm = FastMail(conf)
#     await fm.send_message(message)
#     return JSONResponse(status_code=200, content={"message":"email has been sent"})




