from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
import jwt
from server.database.database import get_db
from server.model.auth.access_token import ALGORITHM, SECRET_KEY
from server.repo.auth.access_token_repository_impl import AccessTokenRepositoryImpl
from server.repo.auth.refresh_token_repository_impl import RefreshTokenRepositoryImpl
from server.repo.auth.user_repository_impl import UserRepositoryImpl
from server.services.auth.user_service import UserService
from server.services.auth.token_service import TokenService
from sqlalchemy.orm import Session

db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_user_service(db: db_dependency) -> UserService:
    user_repository = UserRepositoryImpl(db)
    user_service = UserService(user_repository)
    return user_service


def get_token_service(db: db_dependency) -> TokenService:
    user_repository = UserRepositoryImpl(db)
    access_token_repository = AccessTokenRepositoryImpl(db)
    refresh_token_repository = RefreshTokenRepositoryImpl(db)
    token_service = TokenService(
        access_token_repository, refresh_token_repository, user_repository
    )
    return token_service


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
user_service_dependency = Annotated[UserService, Depends(get_user_service)]
token_service_dependency = Annotated[TokenService, Depends(get_token_service)]
