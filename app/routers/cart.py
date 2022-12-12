from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException, status, Response
from typing import List
from sqlmodel import Session, select
from typing import Dict
from app import models, util, file, auth2
from app.db import get_session
from app.config import setting

router = APIRouter(
    tags= ["CARTS"]
)



@router.post("/users/buy", response_model= models.ProductReturn)
async def add_to_cart(quantity: models.Quantity, product_id: int, user: models.User = Depends(auth2.get_current_user), db: Session = Depends(get_session)):

    product = await db.execute((select(models.Product)).where(models.Product.product_id == product_id))

    product: None | models.Product = product.scalars().first()

    if quantity.quantity < 1:
        raise HTTPException(status_code= 204, detail= f"You haven't select the quantity you want yet")

    if product.quantity < quantity.quantity:
        raise HTTPException(status_code= 409, detail = f"We only have {product.quantity} of this product left in the store")
    
    dict_product = product.copy(exclude = {"quantity","user_id", "created_at"})
    dict_product = dict_product.dict()
    dict_product["quantity"] = quantity.quantity
    dict_product["user_email"] = user.email
    cart: models.Cart = models.Cart(**dict_product)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart

@router.get("/users/cart", response_model= List[models.ProductReturn])
async def my_cart_list(user: models.User = Depends(auth2.get_current_user), db: Session = Depends(get_session)):
    carts = await db.execute((select(models.Cart)).where(models.Cart.user_email == user.email))
    
    carts: models.Cart | None = carts.scalars().all()

    if not carts:
        raise HTTPException(status_code= 204, detail = f"You do not have any product in cart")
    return carts

@router.delete("/users/cart/delete/{product_id}", status_code= 204)
async def remove_from_cart(product_id: int, user: models.User = Depends(auth2.get_current_user), db: Session = Depends(get_session)):

    product = await db.execute((select(models.Cart)).where(models.Cart.product_id == product_id).where(models.Cart.user_email == user.email))

    product: models.Cart | None = product.scalars().first()

    if not product:
        raise HTTPException(status_code= 204, detail= f"No content")
    await db.delete(product)
    await db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)

