from sqlmodel import Field, Relationship
from .db import SQLModel
from typing import List, Optional
from sqlalchemy import Integer,ForeignKey, Column,String, Boolean
from typing import Optional
from datetime import datetime
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from pydantic import EmailStr
from pydantic.types import PositiveFloat
from app.paystack import PayStack

class Base(SQLModel):
    username: str
    email: EmailStr
    password: str

class User(SQLModel, table = True):

    id: Optional[int] = Field(default=None, primary_key = True)
    username: str = Field(sa_column=Column(String, nullable = False))
    email: str = Field(sa_column=Column(String, unique=True, nullable = False))
    password: str = Field(sa_column=Column(String, nullable = False))
    is_verified: Optional[bool] = Field(sa_column= Column(Boolean, server_default= "false"))
    created_at: Optional[datetime] = Field(sa_column= Column(TIMESTAMP(timezone=True), 
    server_default=text("now()")))
    #products: List["Product"] = Relationship(back_populates="owner")

class UserCreate(Base):
    confirm_password: str

class TokenData(SQLModel):
    email: EmailStr

class LoginReturn(SQLModel):

    access_token: str
    token_type: str = "bearer"

class ForgetPassword(SQLModel):
    email: EmailStr


"""class ProductList(SQLModel):
    product_name: str
    image : str
    category: str
    flash_sales: bool = False
    new_arrival: bool = False"""


class ProductCreate(SQLModel):
    category: str
    product_name: str
    price: float
    new_arrival: bool = False
    flash_sales: bool = False
    discount: Optional[float] = None
    image: str
    image1: Optional[str] = None
    image2: Optional[str] = None
    description: Optional[str] = None
    quantity: int


class Product(ProductCreate, table= True):
    product_id: Optional[int] = Field(default= None, primary_key= True)
    created_at: Optional[datetime] = Field(sa_column= Column(TIMESTAMP(timezone=True), 
    server_default=text("now()")))
    user_id: int = Field(sa_column= Column(Integer, 
    ForeignKey("user.id", ondelete="CASCADE"), nullable= True), default = None)
    

class ProductReturn(ProductCreate):
    product_id: int
    created_at: datetime

class UpdatePassword(SQLModel):
    old_password: str
    new_password: str

class PlainMessage(SQLModel):
    detail: str

class Cart(ProductCreate, table = True):
    cart_id: Optional[int] = Field(default= None, primary_key= True)
    user_email: EmailStr 
    created_at: Optional[datetime] = Field(sa_column= Column(TIMESTAMP(timezone=True), 
    server_default=text("now()")))
    product_id: int
    quantity: int

class Quantity(SQLModel):
    quantity: int

class ProductUpdate(SQLModel):
    category: Optional[str] = None
    product_name: Optional[str] = None
    price: Optional[float] = None
    new_arrival: Optional[bool] = None
    flash_sales: Optional[bool] = None
    discount: Optional[float] = None
    image: Optional[str] = None
    image1: Optional[str] = None
    image2: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None




class Payment(SQLModel):
    
    user_email: EmailStr 
    amount: PositiveFloat
    ref: str 


    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            print(status)
          
            if result["amount"]  == self.amount:
                print(result["amount"] / 100 )
                print(self.amount)
                return True
        return False

class Payment2(Payment):

    id: int
    quantity: int
    
        

class Receipt(SQLModel):
    quantity: int
    product_name: str
    price: float
    discount: Optional[int] = 0
    category: str
 
    








