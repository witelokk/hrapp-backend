from datetime import datetime, timedelta, UTC
from hashlib import sha256
import re
from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, Form, HTTPException, status
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
ACCESS_TOKEN_EXPIRES_AFTER = timedelta(minutes=10)
REFRESH_TOKEN_EXPIRES_AFTER = timedelta(days=100)

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
    refresh_token: str
    token_type: str


class TokenRequestForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password|refresh_token"),
        username: str = Form(default=""),
        password: str = Form(default=""),
        refresh_token: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.refresh_token = refresh_token


def get_current_user(
    token: Annotated[
        str,
        Depends(
            oauth2_bearer,
        ),
    ]
):
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


@router.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"model": None, "description": "user exists"}},
)
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
    form_data: Annotated[TokenRequestForm, Depends()], db: db_dependency
) -> Token:
    if form_data.grant_type == "password":
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid credentials")
    elif form_data.grant_type == "refresh_token":
        models.RefreshToken.delete_expired_tokens()
        refresh_token = (
            db.query(models.RefreshToken)
            .filter_by(token_hash=sha256(form_data.refresh_token.encode()).hexdigest())
            .first()
        )

        if not refresh_token:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid refresh token")

        db.delete(refresh_token)
        user = refresh_token.user
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid grant type")

    access_token = jwt.encode(
        {
            "id": user.id,
            "expire": (datetime.now(UTC) + ACCESS_TOKEN_EXPIRES_AFTER).timestamp(),
        },
        SECRET_KEY,
        ALGORITHM,
    )

    refresh_token = uuid4().hex
    db_refresh_token = models.RefreshToken(
        token_hash=sha256(refresh_token.encode()).hexdigest(),
        expires=(datetime.now(UTC) + REFRESH_TOKEN_EXPIRES_AFTER),
        user=user,
    )
    db.add(db_refresh_token)
    db.commit()

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


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
