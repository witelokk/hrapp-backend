from server.repo.auth.user_repository import UserRepository
from server.repo.auth.access_token_repository import AccessTokenRepository
from server.repo.auth.refresh_token_repository import RefreshTokenRepository


class InvalidPasswordError(Exception):
    pass


class UserDoesNotExistError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class InvalidRefreshToken(Exception):
    pass


class TokenService:
    def __init__(
        self,
        access_token_repository: AccessTokenRepository,
        refresh_token_repository: RefreshTokenRepository,
        user_repository: UserRepository,
    ):
        self._access_token_repository = access_token_repository
        self._refresh_token_repository = refresh_token_repository
        self._user_repository = user_repository

    def create_token(self, email: str, password: str):
        user = self._user_repository.find_user_by_email(email)

        if not user:
            raise UserDoesNotExistError()

        if not user.validate_password(password):
            raise InvalidPasswordError()

        access_token = self._access_token_repository.create_access_token(user.id).token
        refresh_token = self._refresh_token_repository.create_refresh_token(user.id)

        return access_token, refresh_token

    def refresh_token(self, token: str):
        refresh_token = self._refresh_token_repository.get_refresh_token(token)

        if not refresh_token:
            raise InvalidRefreshToken()

        access_token = self._access_token_repository.create_access_token(
            refresh_token.user_id
        ).token
        new_refresh_token = self._refresh_token_repository.create_refresh_token(
            refresh_token.user_id
        )

        self._refresh_token_repository.delete_refresh_token(token)

        return access_token, new_refresh_token
