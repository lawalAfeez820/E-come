
from typing import Optional, List
from . import models
from app.db import get_session
from sqlmodel import SQLModel, Session, select
from pydantic import EmailStr
from jose import jwt, JWTError
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
import secrets
from app.config import setting


class EmailSchema(SQLModel):
    email: EmailStr

SECRET = setting.secret
ALGORITHM = setting.algorithm
EXP = setting.expiry_time



#mail = EmailSchema(email ="lawalafeez820@gmail.com")

#use = 2



# Create message container - the correct MIME type is multipart/alternative.
def send_email(user =  models.User):
    token_data = {
            "email": user.email
        }

    expire = datetime.utcnow() + timedelta(minutes=EXP)

    token_data.update({"exp":expire})

    token = jwt.encode(token_data, SECRET, algorithm=ALGORITHM)
    

    # me == my email address
    # you == recipient's email address
    me = setting.email
    you = user.email
    password =setting.email_password
   
    



    html = f"""\
        <!DOCTYPE html>
            <html>
            <head>
            </head>
            <body>
            
            <div>
            <p>
            Thank you for choosing this e-commerce, please click on the link below
            to verify your account. <br />
            The link expires in thirty minutes time
            </p>
            <a
            target="_blank"
            rel="noopener noreferrer"
            href="{setting.localhost}/verification/?token={token}"
            >
            Click here to verify your account
            </a>
            <br/>
            <small>
            If you did not register on this platform, kindly disregard this
            message
            </small>
        </div>
            </body>
            </html>
        """
    msg = MIMEMultipart()

    msg['Subject'] = "Verification mail"
    msg['From'] = me
    msg['To'] = you

    msg.attach(MIMEText(html,"html"))
    msg_string = msg.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",465, context=context) as server:
        server.login(me, password)
        server.sendmail(me, you, msg_string)


def verify_token(token,CredentialException):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])

        email: str = payload.get("email")

        if not email:
            raise CredentialException
        token_data = models.TokenData(email=email)
    except JWTError as e:
        raise CredentialException
    return token_data

async def get_user(token):
    redentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    
    token_data= verify_token(token, redentials_exception)



    return token_data


password = secrets.token_hex(8)
def get_new_password(email: EmailStr):

    me = setting.email
    you = email
    _password =setting.email_password
   


    html = f"""\
    <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div>
                <p>Your new password is {password}</p>
              
            </div>
        </body>
        </html>
    """
    msg = MIMEMultipart()

    msg['Subject'] = "New Password Notification"
    msg['From'] = me
    msg['To'] = you

    msg.attach(MIMEText(html,"html"))
    msg_string = msg.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",465, context=context) as server:
        server.login(me, _password)
        server.sendmail(me, you, msg_string)







