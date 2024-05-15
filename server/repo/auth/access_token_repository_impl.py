from sqlalchemy.orm import Session

from server.model.auth.access_token import AccessToken


class AccessTokenRepositoryImpl:
    def __init__(self, db: Session):
        self._db = db

    def create_access_token(self, user_id: int) -> AccessToken:
        return AccessToken.new(user_id)
