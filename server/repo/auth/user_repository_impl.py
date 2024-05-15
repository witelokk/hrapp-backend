from sqlalchemy.orm import Session

from server.database.models import User as DbUser
from server.model.auth.user import User


class UserRepositoryImpl:
    def __init__(self, db: Session):
        self._db = db

    def create_user(self, email: str, password_hash: str) -> int:
        db_user = DbUser(email=email, password_hash=password_hash)
        self._db.add(db_user)
        self._db.commit()
        return db_user

    def get_user(self, user_id: int):
        pass

    def find_user_by_email(self, email: str) -> User:
        db_user = self._db.query(DbUser).filter_by(email=email).one_or_none()

        if not db_user:
            return None

        return User(
            id=db_user.id, email=db_user.email, password_hash=db_user.password_hash
        )

    def delete_user(self, user_id: int):
        self._db.query(DbUser).filter_by(id=user_id).delete()
        self._db.commit()
