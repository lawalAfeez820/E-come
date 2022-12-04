from fastapi import  Depends, APIRouter, HTTPException, status, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuthError

from sqlmodel import Session, select
from typing import Dict, Optional, List
from app import models, auth2, util, file
from app.db import get_session
from app.config import setting
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import requests as re
import socket
from pydantic import EmailStr


router = APIRouter(
    tags= ["GOOGLE LOGIN"]
)



config = Config('.env')  # read config from .env file
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',

    },
    client_id=setting.client_id,
    client_secret=setting.client_secret

)

@router.get('/login/google')
async def login(request: Request):
    # absolute url for callback
    # we will define it below
    redirect_uri = request.url_for('auth')
    try:
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail = "Kindly check your internet connection")



@router.get('/auth', response_model=models.LoginReturn)
async def auth(background_tasks: BackgroundTasks,request: Request,  db: Session= Depends(get_session)):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    try:
        user_data = await oauth.google.parse_id_token(request, access_token)
    except:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail = "Kindly check your internet connection")
    # TODO: validate email in our database and generate JWT token
    user_email= user_data["email"]
    query = await db.execute(select(models.User).where(models.User.email == user_email))
    query= query.scalars().first()
    if not query:
        user = {"username":user_data['given_name'], "password":user_data['name'], 
        "email": user_data['email'], "is_verified": True}
        user["password"] = util.hash(user["password"])
        
        user = models.Base(**user)
        
        user = models.User.from_orm(user)
        db.add(user)
        await db.commit()
        if user and not user.is_verified:
            user.is_verified = True
            db.add(user)
            await db.commit()
            await db.refresh(user)
    token = auth2.get_access_token({"email": user_data["email"]})
    # TODO: return the JWT token to the user so it can make requests to our /api endpoint
    return models.LoginReturn(access_token = token, token_type = "bearer")

@router.get('/logout')
def logout(request: Request):
    request.session.pop('user', None) 
    return RedirectResponse(url='/')