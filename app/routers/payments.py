from app.logic.logic import PaymentSession

from fastapi import  Depends, APIRouter, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse

from sqlmodel import Session, select
from typing import Dict, Optional, List
from app import models, auth2
from app.db import get_session
from app.config import setting
import secrets
from typing import Tuple, List

from pydantic import EmailStr



router = APIRouter(
    tags= ["Total Payment"],
    prefix= "/pay"
)

@router.get("/all")
async def pay_cart_1(user: models.User = Depends(auth2.get_current_user), db: Session = Depends(get_session)):
    
    
    Total, products = await PaymentSession.total(email= user.email, db= db)

    return {"Total Price": Total, "Products": products}

@router.get("/now/{id}")
async def pay_cart_2(id: int, quantity: int, user: models.User = Depends(auth2.get_current_user), db: Session = Depends(get_session)):

    Total, products = await PaymentSession.buy_directly(id=id, quantity= quantity, db= db)

    return {"Total Price": Total, "Products": products}

@router.get("/{ref}/{amount}{quantity}/{id}/{email}")
async def verify(ref: str, id: int, email:EmailStr, quantity: int, amount:float, db: Session = Depends(get_session)):

    payment= models.Payment2(amount=amount, user_email=email, ref=ref, id=id, quantity=quantity)
    if payment.verify_payment():
            query2 = await db.execute((select(models.Product)).where(models.Product.product_id == id))
            query2: models.Product = query2.scalars().first()
            query2.quantity -= quantity
            db.add(query2)
            await db.commit()
            await db.refresh(query2)
            return RedirectResponse(url='/', status_code=204)
    return JSONResponse({"detail": "Unsuccessful Transaction"})

@router.get("/{ref}/{amount}/{email}")
async def verify_cart(ref: str, email: EmailStr, amount:float, db: Session = Depends(get_session)):

    
    payment = models.Payment(amount=amount, user_email=email, ref=ref)
    if payment.verify_payment():
        query = await db.execute((select(models.Cart)).where(models.Cart.user_email == email))
        query: List[models.Cart]= query.scalars().all()
        for product in query:
            query2 = await db.execute((select(models.Product)).where(models.Product.product_id == product.product_id))
            query2: models.Product = query2.scalars().first()
            query2.quantity -= product.quantity
            db.add(query2)
            await db.delete(product)
        await db.commit()
        return RedirectResponse(url='/', status_code=204)
    return JSONResponse({"detail": "Unsuccessful Transaction"})




    








