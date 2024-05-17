from datetime import datetime
from enum import Enum
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel, StringConstraints

from server.api.dependenicies import user_dependency
from server.api.dependenicies import user_dependency, db_dependency
from server.database import models

router = APIRouter(prefix="/employees", tags=["employees"])


class CurrentInfo(BaseModel):
    position: str
    department_id: int
    salary: float


class EmployeeGender(str, Enum):
    male = "male"
    female = "female"


class Employee(BaseModel):
    id: int
    name: str
    gender: EmployeeGender
    birthdate: datetime
    inn: Annotated[str, StringConstraints(min_length=12, max_length=12, pattern="\d+")]
    snils: Annotated[str, StringConstraints(min_length=11, max_length=11, pattern="\d+")]
    address: str
    passport_number: Annotated[str, StringConstraints(min_length=10, max_length=10, pattern="\d+")]
    passport_date: datetime
    passport_issuer: str
    current_info: CurrentInfo | None

    @classmethod
    def from_sqlalchemy_model(cls, employee: models.Employee) -> "Employee":
        current_position = employee.current_position
        current_department = employee.current_department
        current_salary = employee.current_salary

        if not any((current_position, current_department, current_salary)):
            current_info = None
        else:
            current_info = CurrentInfo(
                position=current_position,
                department_id=current_department.id,
                salary=current_salary,
            )

        return cls(
            id=employee.id,
            name=employee.name,
            gender=employee.gender,
            birthdate=employee.birthdate,
            inn=employee.inn,
            snils=employee.snils,
            address=employee.address,
            passport_number=employee.passport_number,
            passport_date=employee.passport_date,
            passport_issuer=employee.passport_issuer,
            current_info=current_info,
        )


class CreateEmployeeRequest(BaseModel):
    name: str
    gender: EmployeeGender
    birthdate: datetime
    inn: Annotated[str, StringConstraints(min_length=12, max_length=12, pattern="\d+")]
    snils: Annotated[str, StringConstraints(min_length=11, max_length=11, pattern="\d+")]
    address: str
    passport_number: Annotated[str, StringConstraints(min_length=10, max_length=10, pattern="\d+")]
    passport_date: datetime
    passport_issuer: str



class EditEmployeeRequest(BaseModel):
    name: str


@router.get("/company/{company_id}")
def get_employees_by_company(
    db: db_dependency, user: user_dependency, company_id: int
) -> list[Employee]:
    company = db.query(models.Company).filter_by(id=company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employees = db.query(models.Employee).all()
    return [
        Employee.from_sqlalchemy_model(employee)
        for employee in employees
        if employee.current_company == company
    ]


@router.get("/department/{department_id}")
def get_employees_by_department(
    db: db_dependency, user: user_dependency, department_id: int
) -> list[Employee]:
    department = db.query(models.Department).filter_by(id=department_id).first()

    if department is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Department does not exist")

    if department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employees = db.query(models.Employee).filter_by(owner_id=user["id"]).all()
    return [
        Employee.from_sqlalchemy_model(employee)
        for employee in employees
        if employee.current_department == department
    ]


@router.get("/{employee_id}")
def get_employee(
    db: db_dependency, user: user_dependency, employee_id: int
) -> Employee:
    employee = db.query(models.Employee).filter_by(id=employee_id).first()

    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if employee.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Employee.from_sqlalchemy_model(employee)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_employee(
    db: db_dependency, user: user_dependency, request: CreateEmployeeRequest
) -> Employee:
    employee = models.Employee(name=request.name, owner_id=user["id"])
    db.add(employee)
    db.commit()
    return Employee.from_sqlalchemy_model(employee)


@router.patch("/{employee_id}")
def delete_employee(
    db: db_dependency,
    user: user_dependency,
    employee_id: int,
    edit_employee_request: EditEmployeeRequest,
):
    employee = db.query(models.Employee).filter_by(id=employee_id).first()

    if employee is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Employee does not exist")

    if employee.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employee.name = edit_employee_request.name
    db.commit()


@router.delete("/{employee_id}")
def delete_employee(db: db_dependency, user: user_dependency, employee_id: int):
    employee = db.query(models.Employee).filter_by(id=employee_id).first()

    if employee is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Employee does not exist")

    if employee.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    db.delete(employee)
    db.commit()