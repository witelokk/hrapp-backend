from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel


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
