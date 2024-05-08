from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel

from . import auth

from .. import models
from ..database import db_dependency

router = APIRouter(prefix="/departments", tags=["departments"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class Department(BaseModel):
    id: int
    name: str
    company_id: int


class CreateDepartmentRequest(BaseModel):
    name: str
    company_id: int


class EditDepartmentRequest(BaseModel):
    name: str = None
    company_id: int = None


@router.get("/{department_id}")
def get_department(
    db: db_dependency, user: user_dependency, department_id: int
) -> Department:
    department = db.query(models.Department).filter_by(id=department_id).first()

    if department is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Department(id=department.id, name=department.name)


@router.get("/company/{company_id}")
def get_departments_by_company(
    db: db_dependency, user: user_dependency, company_id: int
) -> list[Department]:
    company = db.query(models.Company).filter_by(id=company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company doesn't exist")

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden company")

    return [
        Department(
            id=department.id, name=department.name, company_id=department.company_id
        )
        for department in company.departments
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_department(
    db: db_dependency, user: user_dependency, request: CreateDepartmentRequest
):
    company = db.query(models.Company).filter_by(id=request.company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    department = models.Department(company_id=request.company_id, name=request.name)
    db.add(department)
    db.commit()


@router.patch("/{department_id}")
def edit_department(
    db: db_dependency,
    user: user_dependency,
    department_id: int,
    edit_department_request: EditDepartmentRequest,
):
    department = db.query(models.Department).filter_by(id=department_id).first()

    if department is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Department does not exist")

    if department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    if edit_department_request.company_id is not None:
        company = (
            db.query(models.Company)
            .filter_by(id=edit_department_request.company_id)
            .first()
        )

        if company is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "New company does not exist"
            )

        if company.owner_id != user["id"]:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        department.company = company

    if edit_department_request.name:
        department.name = edit_department_request.name

    db.commit()


@router.delete("/{department_id}")
def delete_department(db: db_dependency, user: user_dependency, department_id: int):
    department = db.query(models.Department).filter_by(id=department_id).first()

    if department is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Department does not exist")

    if department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    owner_employees = db.query(models.Employee).filter_by(owner_id=user["id"]).all()
    department_employees = [
        employee
        for employee in owner_employees
        if employee.current_department == department
    ]

    for employee in department_employees:
        db.delete(employee)

    db.commit()
