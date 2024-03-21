from fastapi import APIRouter, status, HTTPException, Depends, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from services.dbservices import db_dependency
from services.authservices import bcrpyt, get_current_user,authenticate_user, create_access_token, verify_token
from models import User
from schemas.userschemas import UserBase, Response, Token, EventRoles, Gender, UserProfile
from datetime import datetime
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated
from datetime import timedelta
from fastapi_cache.decorator import cache
from fastapi.templating import Jinja2Templates
from fastapi_limiter.depends import RateLimiter



auth = APIRouter()

templates = Jinja2Templates(directory="templates")

user_dependency = Annotated[dict, Depends(get_current_user)]


# Endpoint to create a user
@auth.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(db: db_dependency, request: UserBase, roles: EventRoles):
    if request.password != request.confirm_password:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail="password not the same, Please try again")
    
    user_model = User(
        username = request.username,
        email = request.email,
        full_name = request.full_name,
        hashed_pasword = bcrpyt.hash(request.password),
        role = roles,
        is_active = True
    )

    db.add(user_model)
    db.commit()

    return Response(message=f"Signup successfull, Welcome {request.full_name}, a verification code will be sent to your email address you provided")


# @auth.get("/verification", response_class=HTMLResponse)
# async def verification_mail(request: Request, token: str, db:db_dependency):
#     user = verify_token(token)
#     # person = db.query(User).filter(User.id == ).first()

#     if user and not user.is_verified:
#         user.is_verified = True
#         await user.save()
#         return templates.TemplateResponse("verify.html", {"request": request, "username": user.username})
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired token", headers={"WWW.Authenticate": "Bearer"})


# Endpoint to login your account
@auth.post("/login", response_model=Token)
async def login_access(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Authentication Failed"
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=55))

    return{
        "access_token": token,
        "token_type": "bearer"
    }


# Endpoint to view user detials
@auth.get("/userprofile/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@cache(expire=240)
async def userprofile(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Login to view your user profile")

    user_profile = db.query(User).filter(User.id == user.get("id")).first()
    if user_profile is not None:
        return user_profile
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This doesn't exist or has not been created yet.")


# Endpoint to set reminder for event



# Endpoint to edit userprofile 
@auth.put("/edit/", status_code=status.HTTP_200_OK)
async def edit_userprofile(user: user_dependency, db: db_dependency, profile: UserProfile, gender: Gender):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user_profile = db.query(User).filter(User.id == user.get("id")).first()
    print(user_profile)
    if user_profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    
    user_profile.gender = gender
    user_profile.country = profile.country
    user_profile.city = profile.city
    user_profile.state = profile.state
    user_profile.created_at = datetime.now()

    db.add(user_profile)
    db.commit()

    return {"Message":"Edited successfully"}



