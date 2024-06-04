from typing import Literal

from server.repo.actions_repository import ActionsRepository
from server.repo.companies_repository import CompaniesRepository
from server.repo.departments_repository import DepartmentsRepository
from server.repo.employees_repository import EmployeesRepository
from server.schemas.departments import Department
from server.schemas.actions import ActionWrapper
from server.schemas.employees import (
    CurrentInfo,
    Employee,
    CreateEmployeeRequest,
    CreatedEmployeeId,
)
from server.services.convert_actions_to_schemas import convert_actions_to_schemas
from .employees_service import (
    EmployeesService,
    EmployeeNotExistsError,
    CompanyNotExistsError,
    DepartmentNotExistsError,
    ForbiddenError,
)
from server.model.employee import Employee as EmployeeModel


def employee_from_model(employee: EmployeeModel, actions: list[ActionWrapper] = None):
    current_position = employee.current_position
    current_department = employee.current_department
    current_salary = employee.current_salary

    if not any((current_position, current_department, current_salary)):
        current_info = None
    else:
        current_info = CurrentInfo(
            position=current_position,
            department=Department(
                id=current_department.id,
                name=current_department.name,
                company_id=current_department.company_id,
            ),
            salary=current_salary,
        )

    return Employee(
        id=employee.id,
        name=employee.name,
        gender=employee.gender,
        birthdate=employee.birthdate,
        inn=employee.inn,
        snils=employee.snils,
        address=employee.address,
        passport_number=employee.passport_number,
        passport_date=employee.passport_date,
        passport_issuer=employee.passport_issuer,
        current_info=current_info,
        actions=actions,
        company_id=employee.last_company_id
    )


def model_from_request(
    create_empolyee_request: CreateEmployeeRequest, owner_id: int
) -> EmployeeModel:
    return EmployeeModel(
        owner_id=owner_id,
        name=create_empolyee_request.name,
        gender=create_empolyee_request.gender,
        birthdate=create_empolyee_request.birthdate,
        inn=create_empolyee_request.inn,
        snils=create_empolyee_request.snils,
        address=create_empolyee_request.address,
        passport_number=create_empolyee_request.passport_number,
        passport_date=create_empolyee_request.passport_date,
        passport_issuer=create_empolyee_request.passport_issuer,
    )


class EmployeesServiceImpl(EmployeesService):
    def __init__(
        self,
        employees_repository: EmployeesRepository,
        companies_repository: CompaniesRepository,
        departments_repository: DepartmentsRepository,
        actions_repository: ActionsRepository,
    ):
        self._employees_repository = employees_repository
        self._companies_repository = companies_repository
        self._departments_repository = departments_repository
        self._actions_repository = actions_repository

    def get_employees_by_company(self, user_id: int, company_id: int) -> list[Employee]:
        company = self._companies_repository.get_company(company_id)

        if company is None:
            raise CompanyNotExistsError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        employees = self._employees_repository.get_employees_by_company(company_id)
        return [employee_from_model(employee) for employee in employees]

    def get_employees_by_department(
        self, user_id: int, department_id: int
    ) -> list[Employee]:
        department = self._departments_repository.get_department(department_id)

        if department is None:
            raise DepartmentNotExistsError()

        if department.owner_id != user_id:
            raise ForbiddenError()

        employees = self._employees_repository.get_employees_by_department(
            department_id
        )
        return [employee_from_model(employee) for employee in employees]

    def get_employee(
        self, user_id: int, employee_id: int, include_actions: bool = False
    ) -> Employee:
        employee = self._employees_repository.get_employee(employee_id)

        if employee is None:
            raise EmployeeNotExistsError()

        if employee.owner_id != user_id:
            raise ForbiddenError()

        if include_actions:
            actions = self._actions_repository.get_actions(employee_id)
        else:
            actions = None

        return employee_from_model(
            employee,
            (
                convert_actions_to_schemas(self._departments_repository, actions)
                if actions
                else None
            ),
        )

    def create_employee(
        self, user_id: int, create_employee_request: CreateEmployeeRequest
    ) -> CreatedEmployeeId:
        employee = model_from_request(create_employee_request, user_id)
        employee_id = self._employees_repository.add_employee(employee)
        return CreatedEmployeeId(id=employee_id)

    def update_employee(
        self,
        user_id: int,
        employee_id: int,
        create_employee_request: CreateEmployeeRequest,
    ) -> None:
        employee = self._employees_repository.get_employee(employee_id)

        if employee is None:
            raise EmployeeNotExistsError()

        if employee.owner_id != user_id:
            raise ForbiddenError()

        employee = model_from_request(create_employee_request, user_id)
        employee.id = employee_id
        self._employees_repository.update_employee(employee)

    def delete_employee(self, user_id: int, employee_id: int):
        employee = self._employees_repository.get_employee(employee_id)

        if employee is None:
            raise EmployeeNotExistsError()

        if employee.owner_id != user_id:
            raise ForbiddenError()

        self._employees_repository.delete_employee(employee_id)
