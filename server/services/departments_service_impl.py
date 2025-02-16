from server.repo.companies_repository import CompaniesRepository
from server.repo.departments_repository import DepartmentsRepository
from server.repo.employees_repository import EmployeesRepository
from server.schemas.departments import (
    Department,
    CreateDepartmentRequest,
    CreatedDepartmentId,
)
from server.services.departments_service import (
    DepartmentsService,
    DepartmentNotExistsError,
    CompanyNotExistsError,
    ForbiddenError,
)
from server.model.department import Department as DepartmentModel


def department_to_schema(department: DepartmentModel) -> Department:
    return Department(
        id=department.id, name=department.name, company_id=department.company_id
    )


class DepartmentsServiceImpl(DepartmentsService):
    def __init__(
        self,
        departments_repository: DepartmentsRepository,
        companies_repository: CompaniesRepository,
        employees_repository: EmployeesRepository
    ):
        self._departments_repository = departments_repository
        self._companies_repository = companies_repository
        self._employees_repository = employees_repository

    def get_department(self, department_id: int, user_id: int) -> Department:
        department = self._departments_repository.get_department(department_id)

        if department is None:
            raise DepartmentNotExistsError()

        if department.owner_id != user_id:
            raise ForbiddenError()

        return department_to_schema(department)

    def get_departments(self, company_id: int, user_id: int) -> list[Department]:
        company = self._companies_repository.get_company(company_id)

        if company is None:
            raise CompanyNotExistsError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        departments = self._departments_repository.get_departments(company_id)
        return [department_to_schema(department) for department in departments]

    def create_department(
        self, create_department_request: CreateDepartmentRequest, user_id: int
    ) -> CreatedDepartmentId:
        company = self._companies_repository.get_company(
            create_department_request.company_id
        )

        if company is None:
            raise CompanyNotExistsError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        department = DepartmentModel(
            owner_id=user_id,
            name=create_department_request.name,
            company_id=create_department_request.company_id,
        )
        department_id = self._departments_repository.add_department(department)

        return CreatedDepartmentId(id=department_id)

    def edit_department(
        self,
        department_id: int,
        create_department_request: CreateDepartmentRequest,
        user_id: int,
    ) -> None:
        company = self._companies_repository.get_company(
            create_department_request.company_id
        )

        if company is None:
            raise CompanyNotExistsError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        department = DepartmentModel(
            id=department_id,
            owner_id=user_id,
            name=create_department_request.name,
            company_id=create_department_request.company_id,
        )
        self._departments_repository.edit_department(department)

    def delete_department(self, department_id: int, user_id: int) -> None:
        department = self._departments_repository.get_department(department_id)

        if department is None:
            raise DepartmentNotExistsError()

        if department.owner_id != user_id:
            raise ForbiddenError()
        
        self._employees_repository.delete_employees_by_department(department_id)
        self._departments_repository.delete_department(department_id)
