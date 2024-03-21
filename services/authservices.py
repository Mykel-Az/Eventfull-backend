from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from models import User
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from services.dbservices import db_dependency
from typing import Annotated
from dotenv import dotenv_values
import jwt as jt



bcrpyt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


config_credentials = dotenv_values(".env")


SECRET_KEY = config_credentials["AUTH_SECRET_KEY"]
ALGORITHM = config_credentials["AUTH_ALGORITHM"]


def authenticate_user(username:str, password:str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrpyt.verify(password, user.hashed_pasword):
        return False
    return user


def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'ctrl': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get("sub")
        user_id = payload.get("id")
        role = payload.get("ctrl")
        if username is None or user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
        return {"username": username, "id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    

async def verify_token(token:str):
    try:
        payload = jt.decode(token, config_credentials['SECRET'], oauth2_bearer)
        user = await User.get( id = payload.get("id"))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW.Authenticate": "Bearer"})
    
    return user
