from datetime import datetime
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel

from . import models, auth
from .database import db_dependency

router = APIRouter(prefix="/employees", tags=["employees"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class CurrentInfo(BaseModel):
    position: str
    department_id: int
    salary: float


class Employee(BaseModel):
    id: int
    name: str
    company_id: int
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
            company_id=employee.company_id,
            current_info=current_info,
        )


class CreateEmployeeRequest(BaseModel):
    name: str
    company_id: int


@router.get("/company/{company_id}")
def get_employees_by_company(
    db: db_dependency, user: user_dependency, company_id: int
) -> list[Employee]:
    company = db.query(models.Company).filter_by(id=company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employees = db.query(models.Employee).filter_by(company=company).all()
    return [Employee.from_sqlalchemy_model(employee) for employee in employees]


@router.get("/department/{department_id}")
def get_employees_by_company(
    db: db_dependency, user: user_dependency, department_id: int
) -> list[Employee]:
    department = db.query(models.Department).filter_by(id=department_id).first()

    if department is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Department does not exist")

    if department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employees = db.query(models.Employee).filter_by(company=department.company).all()
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

    if employee.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Employee.from_sqlalchemy_model(employee)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_employee(
    db: db_dependency, user: user_dependency, request: CreateEmployeeRequest
):
    company = db.query(models.Company).filter_by(id=request.company_id).first()

    if company is None or company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employee = models.Employee(name=request.name, company_id=request.company_id)
    db.add(employee)
    db.commit()
