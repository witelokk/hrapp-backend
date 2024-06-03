from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from server.api.dependenicies import user_dependency, employees_service_dependency
from server.schemas.employees import CreateEmployeeRequest, Employee, CreatedEmployeeId
from server.schemas.error import Error
from server.services.employees_service import (
    EmployeeNotExistsError,
    CompanyNotExistsError,
    DepartmentNotExistsError,
    ForbiddenError,
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "/company/{company_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
    response_model_exclude_none=True,
)
def get_employees_by_company(
    employees_service: employees_service_dependency,
    user: user_dependency,
    company_id: int,
) -> list[Employee]:
    try:
        return employees_service.get_employees_by_company(user["id"], company_id)
    except CompanyNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.get(
    "/department/{department_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
    response_model_exclude_none=True,
)
def get_employees_by_department(
    employees_service: employees_service_dependency,
    user: user_dependency,
    department_id: int,
) -> list[Employee]:
    try:
        return employees_service.get_employees_by_department(user["id"], department_id)
    except DepartmentNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Department does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.get(
    "/{employee_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
    response_model_exclude_none=True,
)
def get_employee(
    employees_service: employees_service_dependency,
    user: user_dependency,
    employee_id: int,
    include_actions: bool = False,
) -> Employee:
    try:
        return employees_service.get_employee(user["id"], employee_id, include_actions)
    except EmployeeNotExistsError:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.post(
    "/",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    employees_service: employees_service_dependency,
    user: user_dependency,
    create_employee_request: CreateEmployeeRequest,
) -> CreatedEmployeeId:
    return employees_service.create_employee(user["id"], create_employee_request)


@router.put(
    "/{employee_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def edit_employee(
    employees_service: employees_service_dependency,
    user: user_dependency,
    employee_id: int,
    create_employee_request: CreateEmployeeRequest,
):
    try:
        employees_service.update_employee(
            user["id"], employee_id, create_employee_request
        )
    except EmployeeNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Employee does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.delete(
    "/{employee_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def delete_employee(
    employees_service: employees_service_dependency,
    user: user_dependency,
    employee_id: int,
):
    try:
        employees_service.delete_employee(user["id"], employee_id)
    except EmployeeNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Employee does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
