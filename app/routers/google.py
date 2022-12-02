from fastapi import  Depends, APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuthError

from sqlmodel import Session, select
from typing import Dict, Optional, List
from app import models, auth2
from app.db import get_session
from app.config import setting
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

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

@router.route('/login/google')
async def login(request: Request):
    # absolute url for callback
    # we will define it below
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)



@router.get('/auth', response_model=models.LoginReturn)
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user_data = await oauth.google.parse_id_token(request, access_token)
    # TODO: validate email in our database and generate JWT token
    token = auth2.get_access_token_for_google_login({"email": user_data["email"]})
    # TODO: return the JWT token to the user so it can make requests to our /api endpoint
    return models.LoginReturn(access_token = token, token_type = "bearer")

@router.get('/logout')
def logout(request: Request):
    request.session.pop('user', None) 
    return RedirectResponse(url='/')