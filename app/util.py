from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password):
    return pwd_context.hash(password)

def verify_hash(current: str, former: str):
    return pwd_context.verify(current, former)