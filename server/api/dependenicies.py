from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
import jwt
from server.database.database import get_db
from server.model.auth.access_token import ALGORITHM, SECRET_KEY
from server.repo.auth.access_token_repository import AccessTokenRepository
from server.repo.auth.access_token_repository_impl import AccessTokenRepositoryImpl
from server.repo.auth.refresh_token_repository import RefreshTokenRepository
from server.repo.auth.refresh_token_repository_impl import RefreshTokenRepositoryImpl
from server.repo.auth.user_repository import UserRepository
from server.repo.auth.user_repository_impl import UserRepositoryImpl
from server.repo.companies_repository import CompaniesRepository
from server.repo.companies_repository_impl import CompaniesRepositoryImpl
from server.services.auth.user_service import UserService
from server.services.auth.token_service import TokenService
from sqlalchemy.orm import Session

from server.services.companies_service import CompaniesService
from server.services.companies_service_impl import CompaniesServiceImpl

db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_user_repository(db: db_dependency) -> UserRepository:
    return UserRepositoryImpl(db)


def get_access_token_repository(db: db_dependency) -> AccessTokenRepository:
    return AccessTokenRepositoryImpl(db)


def get_refresh_token_repository(db: db_dependency) -> RefreshTokenRepository:
    return RefreshTokenRepositoryImpl(db)


def get_companies_repository(db: db_dependency) -> CompaniesRepository:
    return CompaniesRepositoryImpl(db)


access_token_repository_dependency = Annotated[
    UserRepository, Depends(get_access_token_repository)
]
user_repository_dependency = Annotated[
    AccessTokenRepository, Depends(get_user_repository)
]
refresh_token_repository_dependency = Annotated[
    RefreshTokenRepository, Depends(get_refresh_token_repository)
]
companies_repository_dependency = Annotated[
    CompaniesRepository, Depends(get_companies_repository)
]


def get_user_service(user_repository: user_repository_dependency) -> UserService:
    user_service = UserService(user_repository)
    return user_service


def get_token_service(
    user_repository: user_repository_dependency,
    access_token_repository: access_token_repository_dependency,
    refresh_token_repository: refresh_token_repository_dependency,
) -> TokenService:
    return TokenService(
        access_token_repository, refresh_token_repository, user_repository
    )


def get_companies_service(
    companies_repository: companies_repository_dependency,
) -> CompaniesService:
    return CompaniesServiceImpl(companies_repository)


user_service_dependency = Annotated[UserService, Depends(get_user_service)]
token_service_dependency = Annotated[TokenService, Depends(get_token_service)]
companies_service_dependency = Annotated[
    CompaniesService, Depends(get_companies_service)
]


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
