from typing import Literal, Protocol

from server.schemas.employees import CreatedEmployeeId, Employee, CreateEmployeeRequest


class EmployeeNotExistsError(Exception):
    pass


class CompanyNotExistsError(Exception):
    pass


class DepartmentNotExistsError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class EmployeesService(Protocol):
    def get_employees_by_company(self, user_id: int, company_id: int) -> list[Employee]:
        pass

    def get_employees_by_department(
        self, user_id: int, department_id: int
    ) -> list[Employee]:
        pass

    def get_employee(
        self, user_id: int, employee_id: int, include_actions: bool = False
    ) -> Employee:
        pass

    def create_employee(
        self, user_id: int, create_employee_request: CreateEmployeeRequest
    ) -> CreatedEmployeeId:
        pass

    def update_employee(
        self,
        user_id: int,
        employee_id: int,
        create_employee_request: CreateEmployeeRequest,
    ) -> None:
        pass

    def delete_employee(self, user_id: int, employee_id: int):
        pass
