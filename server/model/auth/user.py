from dataclasses import dataclass, field
from passlib.context import CryptContext


@dataclass
class User:
    email: str
    password_hash: str
    id: int = None

    @classmethod
    def new(cls, email: str, password: str) -> "User":
        bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = bcrypt_context.hash(password)

        return cls(email=email, password_hash=password_hash)

    def validate_password(self, password: str) -> bool:
        bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return bcrypt_context.verify(password, self.password_hash)
