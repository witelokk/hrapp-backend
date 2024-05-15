from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from server.settings import get_settings


SECRET_KEY = get_settings().secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_AFTER = timedelta(minutes=10)


@dataclass
class AccessToken:
    user_id: int
    expire: datetime

    @classmethod
    def new(cls, user_id: int):
        return cls(
            user_id=user_id, expire=(datetime.now(UTC) + ACCESS_TOKEN_EXPIRES_AFTER)
        )

    @property
    def token(self):
        return jwt.encode(
            {
                "id": self.user_id,
                "expire": self.expire.timestamp(),
            },
            SECRET_KEY,
            ALGORITHM,
        )

    @property
    def is_valid(self):
        return datetime.now(UTC).timestamp() > self.expire
