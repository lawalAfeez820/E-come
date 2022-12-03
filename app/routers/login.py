from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException, status
import socket
from sqlmodel import Session, select
from typing import Dict
from app import models, util, auth2
from app.db import get_session
from app.config import setting
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags= ["AUTHENTICATION"]
)

@router.post("/login", response_model=models.LoginReturn)
async def login(detail: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):

    query = await db.execute(select(models.User).where(models.User.email == detail.username.lower()))
    query: models.User = query.scalars().first()

    if not query:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = f"Invalid credential")

    if not util.verify_hash(detail.password, query.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = f"Invalid credential")

    if not query.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kindly verify your account")

    token = auth2.get_access_token({"email": query.email})

    token = models.LoginReturn(access_token = token, token_type = "bearer")

    return token