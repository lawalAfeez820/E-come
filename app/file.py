
from typing import Optional, List
from . import models
from app.db import get_session
from sqlmodel import SQLModel, Session, select
from pydantic import EmailStr
from jose import jwt, JWTError
import smtplib
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
            "id": user.id
        }

    expire = datetime.utcnow() + timedelta(minutes=EXP)

    token_data.update({"exp":expire})

    token = jwt.encode(token_data, SECRET, algorithm=ALGORITHM)
    

    # me == my email address
    # you == recipient's email address
    me = "lawalafeez820@gmail.com"
    you = user.email
   
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verification mail"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = """Thanks for choosing This E-commerce, please 
                click on the link below to verify your account\nVerify your email:\nhref="http://localhost:8000/verification/?token={token}"
                \nIf you did not register for this E-commerce, 
                please kindly ignore this email and nothing will happen. Thank"""
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
          The link expires in five minutes
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
           

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP_SSL('smtp.gmail.com')

    mail.ehlo()



    mail.login("lawalafeez820@gmail.com","ldmsdmnvecansbdq")
    mail.sendmail(me, you, msg.as_string())
    mail.quit()


def verify_token(token,CredentialException):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])

        id: str = payload.get("id")

        if not id:
            raise CredentialException
        token_data = models.TokenData(id=id)
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

    # me == my email address
    # you == recipient's email address
    me = "lawalafeez820@gmail.com"
    you = email

    
   
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "New Password Notification"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = text = f"""<p>Your new password is {password}</p>"""
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

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP_SSL('smtp.gmail.com')

    mail.ehlo()



    mail.login("lawalafeez820@gmail.com","ldmsdmnvecansbdq")
    mail.sendmail(me, you, msg.as_string())
    mail.quit()
    







