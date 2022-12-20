from app.db import get_session
from app import models
from typing import List
from fastapi import Depends, HTTPException, status
from sqlmodel import select, Session
from pydantic import EmailStr


class CalculatePayment:

   

    async def total(self, email: EmailStr, db: Session) -> float:

        
        carts = await db.execute((select(models.Cart)).where(models.Cart.user_email == email))

        carts: None | List[models.Cart] = carts.scalars().all()

        if not carts:
            raise HTTPException(status_code= status.HTTP_103_EARLY_HINTS, detail = f"You do not have any item in the cart")

        Total: float = 0

        products = []

        for product in carts:
            prod = models.Receipt(quantity= product.quantity, product_name= product.product_name, price = product.price, 
            discount= product.discount, category= product.category)
            if prod.discount == None:
                prod.discount = 0
            products.append(prod)

            if product.discount:

                payment: float = (product.price - ((product.discount * product.price ) / 100)) * product.quantity
                
                Total += payment
            else:
                Total += (product.price * product.quantity)

        return Total , products

    async def buy_directly(self, id: int, quantity: int, db: Session) -> float:

        buy = await db.execute((select(models.Product)).where(models.Product.product_id == id))

        products = []

        buy: None | models.Product = buy.scalars().first()

        if not buy:
            raise HTTPException(status_code= 204, detail = f"No product")

        if quantity > buy.quantity:
            raise HTTPException(status_code=409, detail= f"We have just {buy.quantity} of this product left")

        Total: float = 0

        prod = models.Receipt(quantity= quantity, product_name= buy.product_name, price = buy.price, 
        discount= buy.discount, category= buy.category)
        if prod.discount == None:
            prod.discount = 0
        products.append(prod)

        if buy.discount:

            payment: float = (buy.price - ((buy.discount * buy.price)/ 100)) * quantity

            Total += payment

        else:
            Total = buy.price * quantity
        return Total, products

PaymentSession = CalculatePayment()
        


        