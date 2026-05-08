from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

def hash(password):
    return pwd_context.hash(password)

def verify(plain, hashed):
    return pwd_context.verify(plain, hashed)