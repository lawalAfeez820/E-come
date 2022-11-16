from sqlmodel import Field
from .db import SQLModel
from typing import List, Optional
from sqlalchemy import Integer,ForeignKey, Column,String, Boolean
from typing import Optional
from datetime import datetime
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from pydantic import EmailStr

class Base(SQLModel):
    username: str
    email: str
    password: str

class User(SQLModel, table = True):

    id: Optional[int] = Field(default=None, primary_key = True)
    username: str = Field(sa_column=Column(String, nullable = False))
    email: str = Field(sa_column=Column(String, unique=True, nullable = False))
    password: str = Field(sa_column=Column(String, nullable = False))
    is_verified: Optional[bool] = Field(sa_column= Column(Boolean, server_default= "false"))
    created_at: Optional[datetime] = Field(sa_column= Column(TIMESTAMP(timezone=True), 
    server_default=text("now()")))

class UserCreate(Base):
    confirm_password: str

class TokenData(SQLModel):
    id: int

class LoginReturn(SQLModel):

    access_token: str
    token_type: str

class ForgetPassword(SQLModel):
    email: EmailStr