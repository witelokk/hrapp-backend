from typing import Protocol
from server.model.auth.access_token import AccessToken


class AccessTokenRepository(Protocol):
    def create_access_token(self, user_id: int) -> AccessToken:
        pass
