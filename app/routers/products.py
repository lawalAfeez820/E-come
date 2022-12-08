from fastapi import  Depends, APIRouter, HTTPException, status

from sqlmodel import Session, select
from typing import Dict, Optional, List
from app import models, auth2
from app.db import get_session
from app.config import setting

from pydantic import EmailStr


router = APIRouter(
    tags= ["PRODUCTS"]
)

@router.post("/products/{email}", status_code= 201, response_model= models.ProductReturn)
async def create_product(email: Optional[EmailStr], product: models.ProductCreate, db: Session = Depends(get_session)):

    if email != setting.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"your are not allow for perform this task")
    product = models.Product.from_orm(product)
    product.category = product.category.lower()
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product 

@router.get("/products",response_model=List[models.ProductReturn])
async def get_all_product(user: models.User = Depends(auth2.get_current_user), db: Session = Depends(get_session)):
    products = await db.execute(select(models.Product))
    
    products = products.scalars().all()
    
    if not products:
        raise HTTPException(status_code= 204, detail= f"No gadget at the moment, PLease check back later")
    return products

@router.get("/products/{category}", response_model= List[models.ProductReturn])
async def get_product_by_category(category: str,user: models.User = Depends(auth2.get_current_user) , db: Session = Depends(get_session)):

    categories = ["phones", "tablets", "laptops", "monitors", "accessories"]
    category = category.lower()
    if category in categories:
        query = await db.execute(select(models.Product).where(models.Product.category == category))
        query = query.scalars().all()
        if not query:
            raise HTTPException(status_code= 204, detail= f"We don't have any product base on this category yet, Please check back later")
        return query
    raise HTTPException(status_code= 204, detail= f"We don't have any product base on this category yet, Please check back later")

@router.get("/product/{id}", response_model= models.ProductReturn)
async def get_product(id: int, db: Session = Depends(get_session),user: models.User= Depends(auth2.get_current_user)):
    product = await db.execute((select(models.Product)).where(models.Product.product_id == id))
    product: None|models.Product = product.scalars().first()

    if not product:
        raise HTTPException(status_code= 204, detail= f" No product with id {id}")

    return product