from datetime import datetime, timedelta, UTC
import re
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..database import db_dependency
from ..settings import get_settings


router = APIRouter(prefix="/auth", tags=["auth"])


SECRET_KEY = get_settings().secret_key
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    email: str
    password: str


class EditUserRequest(BaseModel):
    email: str = None
    password: str = None


class Token(BaseModel):
    access_token: str
    token_type: str


def get_current_user(token: Annotated[str, Depends(oauth2_bearer, )]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["id"]
        expire = payload["expire"]
    except (jwt.DecodeError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    if datetime.now(UTC).timestamp() > expire:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "The token has expired")

    return {"id": user_id}


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/user", status_code=status.HTTP_201_CREATED, responses={status.HTTP_409_CONFLICT: {"model": None, "description": "user exists"}})
def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """Creates a user with given credentials"""
    if db.query(models.User).filter_by(email=create_user_request.email).count():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"A user with the username {create_user_request.email} already exists",
        )

    if not is_email_valid(create_user_request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid email")

    user = models.User(
        email=create_user_request.email,
        password_hash=hash_password(create_user_request.password),
    )

    db.add(user)
    db.commit()


@router.patch("/user")
def edit_user(
    db: db_dependency, user: user_dependency, edit_user_request: EditUserRequest
):
    db_user = db.query(models.User).filter_by(id=user["id"]).first()

    if edit_user_request.email:
        if not is_email_valid(edit_user_request.email):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid email")
        db_user.email = edit_user_request.email

    if edit_user_request.password:
        db_user.password_hash = hash_password(edit_user_request.password)

    db.commit()


@router.delete("/user")
def delete_user(db: db_dependency, user: user_dependency):
    db_user = db.query(models.User).filter_by(id=user["id"]).first()
    db.delete(db_user)
    db.commit()


@router.post("/token")
def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User does not exist")

    access_token = jwt.encode(
        {
            "id": user.id,
            "expire": (datetime.now(UTC) + timedelta(minutes=60)).timestamp(),
        },
        SECRET_KEY,
        ALGORITHM,
    )

    return Token(access_token=access_token, token_type="bearer")


def is_email_valid(email: str):
    return re.match("[^@]+@[^@]+\.[^@]+", email) is not None


def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(models.User).filter_by(email=email).first()

    if not user:
        return None

    if not bcrypt_context.verify(password, user.password_hash):
        return None

    return user
