from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel, StringConstraints

from . import auth

from .. import models
from ..database import db_dependency

router = APIRouter(prefix="/companies", tags=["companies"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class Company(BaseModel):
    id: int
    name: str
    inn: str
    kpp: str


class CreateCompanyRequest(BaseModel):
    name: str
    inn: Annotated[str, StringConstraints(min_length=10, max_length=10)]
    kpp: Annotated[str, StringConstraints(min_length=9, max_length=9)]


class EditCompanyRequest(BaseModel):
    name: str = None
    inn: Annotated[str, StringConstraints(min_length=10, max_length=10)] = None
    kpp: Annotated[str, StringConstraints(min_length=9, max_length=9)] = None


@router.get("")
def get_companies(db: db_dependency, user: user_dependency) -> list[Company]:
    companies = db.query(models.Company).filter_by(owner_id=user["id"]).all()

    return [
        Company(id=company.id, name=company.name, inn=company.inn, kpp=company.kpp)
        for company in companies
    ]


@router.get("/{company_id}")
def get_company(db: db_dependency, user: user_dependency, company_id: int) -> Company:
    company = db.query(models.Company).filter_by(id=company_id).first()

    if company.owner.id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Company(id=company.id, name=company.name, inn=company.inn, kpp=company.kpp)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_company(
    db: db_dependency, user: user_dependency, request: CreateCompanyRequest
):
    company = models.Company(
        owner_id=user["id"], name=request.name, inn=request.inn, kpp=request.kpp
    )
    db.add(company)
    db.commit()


@router.patch("/{company_id}")
def edit_company(
    db: db_dependency,
    user: user_dependency,
    company_id: int,
    edit_company_request: EditCompanyRequest,
):
    company = db.query(models.Companies).filter_by(id=company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    if edit_company_request.name:
        company.name = edit_company_request.name

    if edit_company_request.inn:
        company.inn = edit_company_request.inn

    if edit_company_request.kpp:
        company.kpp = edit_company_request.kpp

    db.commit()


@router.delete("/{company_id}")
def delete_department(db: db_dependency, user: user_dependency, company_id: int):
    company = db.query(models.Companies).filter_by(id=company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    owner_employees = db.query(models.Employee).filter_by(owner_id=user["id"]).all()
    company_employees = [
        employee for employee in owner_employees if employee.current_company == company
    ]

    for employee in company_employees:
        db.delete(employee)

    db.commit()
