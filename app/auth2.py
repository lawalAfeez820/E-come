from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from datetime import datetime, timedelta
from . import models
from app.db import get_session
from fastapi import Depends, status, HTTPException
from sqlmodel import Session
from app.config import setting


EXPIRY_TIME = setting.expiry_time
ALGORITHM =setting.algorithm
SECRET_KEY =setting.secret_key

schema = OAuth2PasswordBearer(tokenUrl = "login")

def get_access_token(payload: Dict):

    expire= datetime.utcnow() + timedelta(minutes=EXPIRY_TIME)
    payload.update({"exp":expire})

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token

def verify_token(token, CredentialException):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        
        id: int =payload.get("id")

        if not id:
            raise CredentialException
        token_data = models.TokenData(id=id)
        
    except JWTError as e:
        raise CredentialException
    return token_data

async def get_current_user(token: str = Depends(schema), db: Session = Depends(get_session)):
    redentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    
    token_data= verify_token(token, redentials_exception)

    user = await db.get(models.User,token_data.id)

    return user

def get_access_token_for_google_login(payload: Dict):

    expire= datetime.utcnow() + timedelta(minutes=EXPIRY_TIME)
    payload.update({"exp":expire})

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


