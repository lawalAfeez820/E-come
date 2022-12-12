from fastapi import  Depends, APIRouter, HTTPException, status, Response

from sqlmodel import Session, select
from typing import Dict, Optional, List
from app import models, auth2
from app.db import get_session
from app.config import setting

from pydantic import EmailStr


router = APIRouter(
    tags= ["ADMIN"]
)

@router.post("/products/{email}", status_code= 201, response_model= models.ProductReturn)
async def create_product(email: Optional[EmailStr], product: models.ProductCreate, db: Session = Depends(get_session)):

    if email != setting.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"you are not allow for perform this task")
    product = models.Product.from_orm(product)
    product.category = product.category.lower()
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product 

@router.put("/products/{email}", status_code= 201, response_model= models.ProductReturn)
async def update_product(email: Optional[EmailStr], id: int, product: models.ProductUpdate, db: Session = Depends(get_session)):

    if email != setting.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"you are not allow for perform this task")

    products = await db.execute((select(models.Product)).where(models.Product.product_id == id))
    products : models.Product = products.scalars().first()
    if not products:
            raise HTTPException(status_code=404, detail="product not found")
    product_data = product.dict(exclude_unset=True)
    for key, value in product_data.items():
        setattr(products, key, value)
    db.add(products)
    await db.commit()
    await db.refresh(products)
    return products


@router.delete("/products/{email}", status_code= 204)
async def delete_product(email: Optional[EmailStr], id: int,  db: Session = Depends(get_session)):

    if email != setting.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"you are not allow for perform this task")

    products = await db.execute((select(models.Product)).where(models.Product.product_id == id))
    products : models.Product = products.scalars().first()
    if not products:
            raise HTTPException(status_code=404, detail="product not found")
    await db.delete(products)
    await db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)


@router.get("/products/all/{email}", status_code= 201, response_model= List[models.ProductReturn])
async def get_all_products(email: Optional[EmailStr], db: Session = Depends(get_session)):

    if email != setting.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"you are not allow for perform this task")

    products = await db.execute((select(models.Product)))
    products : List[models.Product] = products.scalars().all()
    if not products:
            raise HTTPException(status_code=404, detail="product not found")
    return products

@router.get("/products/{email}/{id}", status_code= 201, response_model= models.ProductReturn)
async def get_product(email: Optional[EmailStr], id: int, db: Session = Depends(get_session)):

    if email != setting.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"you are not allow for perform this task")

    products = await db.execute((select(models.Product)).where(models.Product.product_id == id))
    products : models.Product = products.scalars().first()
    if not products:
            raise HTTPException(status_code=404, detail="product not found")
    return products





@router.get("/product/all/{email}", status_code= 201, response_model= List[models.ProductReturn])
async def get_products_by_categories(email: Optional[EmailStr], category: str, db: Session = Depends(get_session)):

    if email != setting.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"you are not allow for perform this task")

    categories = ["phones", "tablets", "laptops", "monitors", "accessories", "string"]
    category = category.lower()
    if category in categories:
        query = await db.execute(select(models.Product).where(models.Product.category == category))
        query = query.scalars().all()
        if not query:
            raise HTTPException(status_code= 204, detail= f"We don't have any product base on this category yet, Please check back later")
        return query
    raise HTTPException(status_code= 204, detail= f"We don't have any product base on this category yet, Please check back later")