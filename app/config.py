from pydantic import BaseSettings

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

    class Config:
        env_file= ".env"

setting = Settings()

