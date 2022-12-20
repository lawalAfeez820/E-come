from pydantic import BaseSettings, EmailStr

class Settings(BaseSettings):
    expiry_time: int
    algorithm: str
    secret_key: str
    database_url: str
    secret: str
    localhost: str
    exp: int
    email: str
    email_password: str
    admin_email: EmailStr
    client_id: str
    client_secret: str
    paystack_public_key: str
    paystack_secret_key: str

    class Config:
        env_file= ".env"

setting = Settings()

