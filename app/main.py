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
import secrets
from app.logic.logic import PaymentSession

from app.routers import google, users, login, products, cart, creator, payments




from fastapi import BackgroundTasks
from typing import Dict

# templates
from fastapi.templating import Jinja2Templates

# HTMLResponse
from fastapi.responses import HTMLResponse


origins = ["*"]




app = FastAPI()



"""app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
allow_headers=["Access-Control-Allow-Headers", 'Content-Type', 'Authorization', 'Access-Control-Allow-Origin'],
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
app.include_router(creator.router)
app.include_router(cart.router)
app.include_router(payments.router)


templates = Jinja2Templates(directory="templates")

@app.get('/verification',  response_class=HTMLResponse)
async def email_verification(request: Request, token: str, db: Session = Depends(get_session)): 
    
    token_data = await file.get_user(token)
    
    user: models.User = await db.execute(select(models.User).where(models.User.email == token_data.email))
    user: models.User= user.scalars().first()
    
    
    if user and not user.is_verified:
        user.is_verified = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return templates.TemplateResponse("verification.html", 
                                {"request": request, "username": user.username})


@app.get("/payment/all")
async def payment_cart(request: Request,  user: models.User = Depends(auth2.get_current_user),  db: Session = Depends(get_session)):

   
    

    Total, products= await PaymentSession.total(email= user.email, db= db)

    payment = models.Payment(user_email= user.email, amount= Total, ref= secrets.token_urlsafe(50))

    return templates.TemplateResponse("make_cart_payment.html", 
                                {"request": request, "payment": payment, "paystack_public_key": setting.paystack_public_key})

@app.get("/payment/now/{id}")
async def pay_now(id: int, request: Request, quantity: int, user: models.User = Depends(auth2.get_current_user), db: Session = Depends(get_session)):

    

    Total, products= await PaymentSession.buy_directly(id=id, quantity= quantity, db= db)


    payment = models.Payment2(id=id, quantity= quantity, user_email=user.email, amount= Total, ref= secrets.token_urlsafe(50))

    return templates.TemplateResponse("make_payment.html",
                                {"request": request, "payment": payment, "paystack_public_key": setting.paystack_public_key})


    


@app.delete("/user/{email}", status_code = 204)
async def delete(email: EmailStr, db: Session = Depends(get_session)):

    query = await db.execute(select(models.User).where(models.User.email == email.lower()))
    query: models.User = query.scalars().first()
    if not query:
        raise HTTPException(status_code= 404, detail =f"User with {email} doesn't exist")
    await db.delete(query)
    await db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)
    




    
