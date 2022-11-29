from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException, status
import socket
from sqlmodel import Session, select
from typing import Dict
from app import models, util, file, auth2
from app.db import get_session
from app.config import setting

router = APIRouter(
    tags= ["USERS"]
)

@router.post("/users", response_model =Dict, status_code = 201)
async def create_user(background_tasks: BackgroundTasks,user: models.UserCreate, db: Session = Depends(get_session)):

    verify = list(user.dict().values())
    
    if not all(verify):
        raise HTTPException(status_code=400, detail= f"One of the field is empty")
    user.email = user.email.lower()
    query = await db.execute(select(models.User).where(models.User.email == user.email))
    query = query.first()
    
    if query:
        raise HTTPException(status_code = 409, detail = f"user with email {user.email} already exist")
    if user.password != user.confirm_password:
        raise HTTPException(status_code = 409, detail = f"password not verified, please enter the same password for the two password field")
    
    user = user.dict()
    del user["confirm_password"]
    user["password"] = util.hash(user["password"])
    user = models.Base(**user)
    user = models.User.from_orm(user)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    try:
        background_tasks.add_task(file.send_email, user)
    except socket.gaierror:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail = "Kindly check your internet connection")
    # background task here
    return {"detail": f"Created successfully, please check your mail for verification. The verification link will expire in {setting.exp} minutes time"}


@router.post("/forgetpassword", status_code=201, response_model= Dict)
async def get_new_password(background_tasks: BackgroundTasks, email: models.ForgetPassword, db: Session = Depends(get_session)):
    
    query = await db.execute(select(models.User).where(models.User.email == email.email.lower()))
    query: models.User = query.scalars().first()

    if not query:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = f"Invalid credential")
    try:
        background_tasks.add_task(file.get_new_password, query.email)
    except socket.gaierror:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail = "Kindly check your internet connection")

    query.password = util.hash(file.password)
    db.add(query)
    await db.commit()
    await db.refresh(query)
    return {"detail": "Check your email for the new password"}

@router.post("/users/updatepassword", response_model=models.PlainMessage)
async def update_password(passwords: models.UpdatePassword, db:Session = Depends(get_session), user: models.User = Depends(auth2.get_current_user)):

    query =await db.execute(select(models.User).where(models.User.email == user.email.lower()))
    query: models.User = query.scalars().first()

    if not util.verify_hash(passwords.old_password, query.password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = "Old password doesn't match")
    passwords.new_password = util.hash(passwords.new_password) 
    query.password = passwords.new_password
    db.add(query)
    await db.commit()
    await db.refresh(query)
    return models.PlainMessage(detail = f"Password has been reset")

    