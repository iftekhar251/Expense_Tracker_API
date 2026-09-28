import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from starlette import status

from database import SessionLocal
from models import Users
from schemas import UserCreate, UserOut, Token

router = APIRouter(prefix='/auth', tags=['auth'])


SECRET_KEY = os.getenv('SECRET_KEY', 'insecure-dev-secret-key-change-me')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta) -> str:
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise credentials_exception
        return {'username': username, 'id': user_id}
    except JWTError:
        raise credentials_exception


@router.post('/register', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(db: db_dependency, user_request: UserCreate):
    existing = db.query(Users).filter(
        (Users.username == user_request.username) | (Users.email == user_request.email)
    ).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username or email already registered')

    user_model = Users(
        username=user_request.username,
        email=user_request.email,
        hashed_password=bcrypt_context.hash(user_request.password),
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    return user_model


@router.post('/login', response_model=Token)
def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')

    token = create_access_token(user.username, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'access_token': token, 'token_type': 'bearer'}
