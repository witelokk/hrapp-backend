from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from server.schemas.companies import (
    Company,
    CreateCompanyRequest,
    EditCompanyRequest,
    CreatedCompanyId,
)
from server.schemas.error import Error
from server.api.dependenicies import user_dependency, companies_service_dependency
from server.database import models
from server.services.companies_service import CompanyNotExistError, ForbiddenError

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get(
    "/",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def get_companies(
    companies_service: companies_service_dependency,
    user: user_dependency,
) -> list[Company]:
    companies = companies_service.get_companies(user["id"])

    return [
        Company(id=company.id, name=company.name, inn=company.inn, kpp=company.kpp)
        for company in companies
    ]


@router.get(
    "/{company_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def get_company(
    companies_service: companies_service_dependency,
    user: user_dependency,
    company_id: int,
) -> Company:
    try:
        company = companies_service.get_company(user["id"], company_id)
    except CompanyNotExistError:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return Company(id=company.id, name=company.name, inn=company.inn, kpp=company.kpp)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def create_company(
    companies_service: companies_service_dependency,
    user: user_dependency,
    request: CreateCompanyRequest,
) -> CreatedCompanyId:
    company_id = companies_service.create_company(
        request.name, request.inn, request.kpp, user["id"]
    )
    return CreatedCompanyId(id=company_id)


@router.patch(
    "/{company_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
    },
)
def edit_company(
    companies_service: companies_service_dependency,
    user: user_dependency,
    company_id: int,
    edit_company_request: EditCompanyRequest,
) -> None:
    try:
        companies_service.edit_company(
            user["id"],
            company_id,
            name=edit_company_request.name,
            inn=edit_company_request.inn,
            kpp=edit_company_request.kpp,
        )
    except CompanyNotExistError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


# @router.delete(
#     "/{company_id}",
#     responses={
#         status.HTTP_400_BAD_REQUEST: {"model": Error},
#         status.HTTP_401_UNAUTHORIZED: {"model": Error},
#         status.HTTP_403_FORBIDDEN: {"model": Error},
#     },
# )
# def delete_department(
#     companies_service: companies_service_dependency,
#     user: user_dependency,
#     company_id: int,
# ):
#     company = db.query(models.Companies).filter_by(id=company_id).first()

#     if company is None:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")

#     if company.owner_id != user["id"]:
#         raise HTTPException(status.HTTP_403_FORBIDDEN)

#     owner_employees = db.query(models.Employee).filter_by(owner_id=user["id"]).all()
#     company_employees = [
#         employee for employee in owner_employees if employee.current_company == company
#     ]

#     for employee in company_employees:
#         db.delete(employee)

#     db.commit()
