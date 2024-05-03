from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel

from . import auth

from .. import models
from ..database import db_dependency

router = APIRouter(prefix="/companies", tags=["companies"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class Company(BaseModel):
    id: int
    name: str


class CreateCompanyRequest(BaseModel):
    name: str


@router.get("/")
def get_companies(db: db_dependency, user: user_dependency) -> list[Company]:
    companies = db.query(models.Company).filter_by(owner_id=user["id"]).all()

    return [Company(id=company.id, name=company.name) for company in companies]


@router.get("/{company_id}")
def get_company(db: db_dependency, user: user_dependency, company_id: int) -> Company:
    company = db.query(models.Company).filter_by(id=company_id).first()

    if company.owner.id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Company(id=company.id, name=company.name)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_company(
    db: db_dependency, user: user_dependency, request: CreateCompanyRequest
):
    company = models.Company(owner_id=user["id"], name=request.name)
    db.add(company)
    db.commit()
