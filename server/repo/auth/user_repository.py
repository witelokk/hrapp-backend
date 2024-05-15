from typing import Protocol

from server.model.auth.user import User


class UserRepository(Protocol):
    def create_user(self, email: str, password_hash: str) -> User:
        pass

    def get_user(self, user_id: int) -> User:
        pass

    def find_user_by_email(self, email: str) -> User:
        pass

    def delete_user(self, user_id: int) -> None:
        pass
