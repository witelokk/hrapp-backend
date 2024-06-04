from dataclasses import dataclass
import datetime

from server.database.models import Department


@dataclass
class Employee:
    owner_id: int
    name: str
    gender: str
    birthdate: datetime.date
    inn: str
    snils: str
    address: str
    passport_number: str
    passport_date: datetime.date
    passport_issuer: str
    last_company_id: int = None
    id: int = None
    current_position: str | None = None
    current_department: Department | None = None
    current_salary: float | None = None