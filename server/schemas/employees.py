import datetime
from typing import Annotated
from enum import Enum

from pydantic import BaseModel, StringConstraints

from server.schemas.actions import ActionWrapper
from server.schemas.departments import Department


class CurrentInfo(BaseModel):
    position: str
    department: Department
    salary: float


class EmployeeGender(str, Enum):
    male = "male"
    female = "female"


class Employee(BaseModel):
    id: int
    name: str
    gender: EmployeeGender
    birthdate: datetime.date
    inn: Annotated[str, StringConstraints(min_length=12, max_length=12, pattern="\d+")]
    snils: Annotated[
        str, StringConstraints(min_length=11, max_length=11, pattern="\d+")
    ]
    address: str
    passport_number: Annotated[
        str, StringConstraints(min_length=10, max_length=10, pattern="\d+")
    ]
    passport_date: datetime.date
    passport_issuer: str
    current_info: CurrentInfo | None
    actions: list[ActionWrapper] | None = None


class CreatedEmployeeId(BaseModel):
    id: int


class CreateEmployeeRequest(BaseModel):
    name: str
    gender: EmployeeGender
    birthdate: datetime.date
    inn: Annotated[str, StringConstraints(min_length=12, max_length=12, pattern="\d+")]
    snils: Annotated[
        str, StringConstraints(min_length=11, max_length=11, pattern="\d+")
    ]
    address: str
    passport_number: Annotated[
        str, StringConstraints(min_length=10, max_length=10, pattern="\d+")
    ]
    passport_date: datetime.date
    passport_issuer: str
