from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status

from server.schemas.auth import CreateUserRequest, Token, TokenRequestForm
from server.api.dependenicies import (
    user_service_dependency,
    token_service_dependency,
    user_dependency,
)
from server.services.auth.token_service import (
    InvalidPasswordError,
    InvalidRefreshToken,
    UserDoesNotExistError,
)
from server.services.auth.user_service import InvalidEmail, UserAlreadyExistsError
from server.api.dependenicies import user_dependency


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"model": None, "description": "User already exists"}
    },
)
def create_user(
    user_service: user_service_dependency, create_user_request: CreateUserRequest
):
    """Creates a user with given email and password"""
    try:
        user_service.create_user(
            create_user_request.email, create_user_request.password
        )
    except UserAlreadyExistsError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"A user with the username {create_user_request.email} already exists",
        )
    except InvalidEmail:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid email")


@router.delete("/user")
def delete_user(user_service: user_service_dependency, user: user_dependency):
    user_service.delete_user(user["id"])


@router.post("/token")
def get_token(
    form_data: Annotated[TokenRequestForm, Depends()],
    token_service: token_service_dependency,
) -> Token:
    if form_data.grant_type == "password":
        try:
            access_token, refresh_token = token_service.create_token(
                form_data.username, form_data.password
            )
        except (UserDoesNotExistError, InvalidPasswordError):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Invalid email or password"
            )
    elif form_data.grant_type == "refresh_token":
        try:
            access_token, refresh_token = token_service.refresh_token(
                form_data.refresh_token
            )
        except InvalidRefreshToken:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid refresh token")
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid grant type")

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )
