from fastapi import Depends, FastAPI, HTTPException,BackgroundTasks, Request, status, Response
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from . import models, file, auth2
from app.config import setting
from app.db import get_session, run_async_upgrade
#from app.db import get_session
from . import models, util
from pydantic import EmailStr
from starlette.middleware.sessions import SessionMiddleware

from app.routers import google, users, login, products



from fastapi import BackgroundTasks
from typing import Dict

# templates
from fastapi.templating import Jinja2Templates

# HTMLResponse
from fastapi.responses import HTMLResponse


origins = ["*"]


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="test secret key")

"""@app.on_event("startup")
async def on_startup():
    await run_async_upgrade()"""


@app.get("/")
async def home():
    return {"message": "welcome"}

app.include_router(users.router)
app.include_router(login.router)
app.include_router(products.router)
app.include_router(google.router)


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



@app.delete("/user/{email}", status_code = 204)
async def delete(email: EmailStr, db: Session = Depends(get_session)):

    query = await db.execute(select(models.User).where(models.User.email == email.lower()))
    query: models.User = query.scalars().first()
    if not query:
        raise HTTPException(status_code= 404, detail =f"User with {email} doesn't exist")
    await db.delete(query)
    await db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)
    




    
