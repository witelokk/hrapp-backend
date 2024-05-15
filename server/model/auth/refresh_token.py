from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256

REFRESH_TOKEN_EXPIRES_AFTER = timedelta(days=100)


@dataclass
class RefreshToken:
    token_hash: str
    expires: datetime
    user_id: int
    id: int = None

    @classmethod
    def new(cls, user_id: int, refresh_token: str) -> "RefreshToken":
        expires = datetime.now() + REFRESH_TOKEN_EXPIRES_AFTER
        token_hash = cls.hash_token(refresh_token)
        return cls(token_hash=token_hash, user_id=user_id, expires=expires)

    @staticmethod
    def hash_token(token: str):
        return sha256(token.encode()).hexdigest()
