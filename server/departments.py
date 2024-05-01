from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel

from . import models, auth
from .database import db_dependency

router = APIRouter(prefix="/departments", tags=["departments"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class Department(BaseModel):
    id: int
    name: str
    company_id: int


class CreateDepartmentRequest(BaseModel):
    name: str
    company_id: int


@router.get("/")
def get_departments(db: db_dependency, user: user_dependency) -> list[Department]:
    departments = db.query(models.Department).filter_by(user_id=user["id"]).all()

    return [
        Department(
            id=department.id, name=department.name, company_id=department.company_id
        )
        for department in departments
    ]


@router.get("/{department_id}")
def get_department(
    db: db_dependency, user: user_dependency, department_id: int
) -> Department:
    department = db.query(models.Department).filter_by(id=department_id).first()

    if department.company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Department(id=department.id, name=department.name)


@router.get("/company/{company_id}")
def get_department(
    db: db_dependency, user: user_dependency, company_id: int
) -> list[Department]:
    company = db.query(models.Company).filter_by(id=company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company doesn't exist")

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Forbidden company")

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
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    department = models.Department(company_id=request.company_id, name=request.name)
    db.add(department)
    db.commit()
