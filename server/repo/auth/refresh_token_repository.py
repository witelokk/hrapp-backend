from datetime import timedelta
from sqlalchemy.orm import Session

from server.model.auth.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self._db = db

    def create_refresh_token(self, user_id) -> str:
        pass

    def get_refresh_token(self, token: str) -> RefreshToken:
        pass

    def delete_refresh_token(self, token: str) -> None:
        pass
