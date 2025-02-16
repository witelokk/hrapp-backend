from typing import Protocol
from server.schemas.departments import (
    Department,
    CreateDepartmentRequest,
    CreatedDepartmentId,
)


class DepartmentNotExistsError(Exception):
    pass


class CompanyNotExistsError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class DepartmentsService(Protocol):
    def get_department(self, department_id: int, user_id: int) -> Department:
        pass

    def get_departments(self, company_id: int, user_id: int) -> list[Department]:
        pass

    def create_department(
        self, create_department_request: CreateDepartmentRequest, user_id: int
    ) -> CreatedDepartmentId:
        pass

    def edit_department(
        self,
        department_id: int,
        create_department_request: CreateDepartmentRequest,
        user_id: int,
    ) -> None:
        pass

    def delete_department(self, department_id: int, user_id: int) -> None:
        pass
