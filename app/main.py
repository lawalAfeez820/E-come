from fastapi import Depends, FastAPI, HTTPException,BackgroundTasks, Request, status
from sqlmodel import Session, select
from . import models, file, auth2
from app.db import get_session, run_async_upgrade
from . import models, util
from pydantic import EmailStr
import socket


from fastapi import BackgroundTasks
from typing import Dict

# templates
from fastapi.templating import Jinja2Templates

# HTMLResponse
from fastapi.responses import HTMLResponse

from fastapi.security import OAuth2PasswordRequestForm



app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await run_async_upgrade()

@app.get("/")
async def home():
    return {"message": "welcome"}

@app.post("/users", response_model =Dict, status_code = 201)
async def create_user(background_tasks: BackgroundTasks,user: models.UserCreate, db: Session = Depends(get_session)):
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
    return {"Message": "Successful created, please check your mail for verification"}


templates = Jinja2Templates(directory="templates")

@app.get('/verification',  response_class=HTMLResponse)
async def email_verification(request: Request, token: str, db: Session = Depends(get_session)): 
    
    token_data = await file.get_user(token)
    print(token_data.id)
    user: models.User = await db.execute(select(models.User).where(models.User.id == token_data.id))
    user: models.User= user.scalars().first()
    
    
    if user and not user.is_verified:
        user.is_verified = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(user)
        return templates.TemplateResponse("verification.html", 
                                {"request": request, "username": user.username})

@app.post("/login")
async def login(detail: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):

    query = await db.execute(select(models.User).where(models.User.email == detail.username.lower()))
    query: models.User = query.scalars().first()

    if not query:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"Invalid credential")

    if not util.verify_hash(detail.password, query.password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"Invalid credential")

    if not query.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kindly verify your account")

    token = auth2.get_access_token({"id": query.id})

    token = models.LoginReturn(access_token = token, token_type = "bearer")

    return token

@app.post("/forgetpassword", status_code=201, response_model= Dict)
async def get_new_password(background_tasks: BackgroundTasks, email: models.ForgetPassword, db: Session = Depends(get_session)):
    
    query = await db.execute(select(models.User).where(models.User.email == email.email.lower()))
    query: models.User = query.scalars().first()

    if not query:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"Invalid credential")
    try:
        background_tasks.add_task(file.get_new_password, query.email)
    except socket.gaierror:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail = "Kindly check your internet connection")

    query.password = util.hash(file.password)
    db.add(query)
    await db.commit()
    await db.refresh(query)
    return {"Message": "Check your email for the new password"}
    




    
