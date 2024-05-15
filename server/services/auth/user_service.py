import re
from server.model.auth.user import User
from server.repo.auth.user_repository import UserRepository


class UserAlreadyExistsError(Exception):
    pass


class InvalidEmail(Exception):
    pass


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._repository = user_repository

    def create_user(self, email: str, password: str) -> User:
        if self._repository.find_user_by_email(email=email) is not None:
            raise UserAlreadyExistsError()

        if not self._validate_email(email):
            raise InvalidEmail()

        user = User.new(email, password)
        db_user = self._repository.create_user(user.email, user.password_hash)
        user.id = db_user.id
        return user

    def delete_user(self, user_id) -> None:
        self._repository.delete_user(user_id)

    @staticmethod
    def _validate_email(email: str):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
