from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from typing import Optional
import os

from .database import get_db, DBUser
from .models import UserCreate, User, Token

# Security settings
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security bearer token
security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# OAuth setup
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    client_kwargs={'scope': 'openid email profile'}
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Optional[str] = Depends(oauth2_scheme),
                    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
                    db: Session = Depends(get_db)) -> User:
    if not token and not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token_str = token if token else credentials.credentials
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        subscription_tier=user.subscription_tier
    )

def authenticate_user(db: Session, email: str, password: str) -> Optional[DBUser]:
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, user: UserCreate) -> DBUser:
    db_user = DBUser(
        email=user.email,
        name=user.name,
        hashed_password=get_password_hash(user.password) if user.password else None,
        oauth_provider=user.oauth_provider,
        oauth_id=user.oauth_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
