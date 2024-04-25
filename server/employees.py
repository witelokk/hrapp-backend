from datetime import datetime
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel

from . import models, auth
from .database import db_dependency

router = APIRouter(prefix="/employees", tags=["employees"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class Position(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime | None


class Employee(BaseModel):
    id: int
    name: str
    active: bool
    positions: list[Position]


class CreateEmployeeRequest(BaseModel):
    name: str
    department_id: int
    position: str
    employment_date: datetime


@router.get("/department/{department_id}")
def get_employees(
    db: db_dependency, user: user_dependency, department_id: int
) -> list[Employee]:
    department = db.query(models.Department).filter_by(id=department_id).first()

    if department is None or department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employees = db.query(models.Employee).filter_by(department_id=department_id).all()

    response = []
    for employee in employees:
        positions = db.query(models.Position).filter_by(employee=employee)
        positions = [
            Position(
                name=position.name,
                start_date=position.start_date,
                end_date=position.end_date,
            )
            for position in positions
        ]
        response.append(
            Employee(
                id=employee.id,
                name=employee.name,
                positions=positions,
                active=positions[-1].end_date is None,
            )
        )

    return response
    # return [Employee(id=company.id, name=company.name, positions=[Position for position in ]) for company in employees]


@router.get("/{employee_id}")
def get_employee(
    db: db_dependency, user: user_dependency, employee_id: int
) -> Employee:
    employee = db.query(models.Employee).filter_by(id=employee_id).first()

    if employee.department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Employee(
        id=employee.id,
        name=employee.name,
        department_id=employee.department_id,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_employee(
    db: db_dependency, user: user_dependency, request: CreateEmployeeRequest
):
    department = db.query(models.Department).filter_by(id=request.department_id).first()

    if department is None or department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    employee = models.Employee(name=request.name, department_id=request.department_id)

    position = models.Position(
        employee=employee,
        name=request.position,
        start_date=request.employment_date,
        end_date=None,
    )

    with db.begin(True) as transaction:
        db.add(employee)
        db.add(position)
        transaction.commit()

    db.commit()
