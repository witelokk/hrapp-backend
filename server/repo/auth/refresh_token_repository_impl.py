from datetime import timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from server.model.auth.refresh_token import RefreshToken
from server.database.models import RefreshToken as DbRefreshToken


class RefreshTokenRepositoryImpl:
    def __init__(self, db: Session):
        self._db = db

    def create_refresh_token(self, user_id: int) -> str:
        refresh_token = uuid4().hex
        token = RefreshToken.new(user_id, refresh_token)
        db_token = DbRefreshToken(
            token_hash=token.token_hash, expires=token.expires, user_id=token.user_id
        )
        self._db.add(db_token)
        self._db.commit()
        return refresh_token

    def get_refresh_token(self, token: str) -> RefreshToken:
        db_token = (
            self._db.query(DbRefreshToken)
            .filter_by(token_hash=RefreshToken.hash_token(token))
            .one_or_none()
        )

        if not db_token:
            return None

        token = RefreshToken(
            id=db_token.id,
            token_hash=db_token.token_hash,
            expires=db_token.expires,
            user_id=db_token.user_id,
        )
        return token

    def delete_refresh_token(self, token: str):
        self._db.query(DbRefreshToken).filter_by(
            token_hash=RefreshToken.hash_token(token)
        ).delete()
        self._db.commit()
