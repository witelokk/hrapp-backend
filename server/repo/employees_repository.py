from typing import Protocol

from server.model.employee import Employee


class EmployeesRepository(Protocol):
    def get_employee(self, employee_id: int) -> Employee:
        pass

    def get_employees_by_company(self, company_id: int) -> list[Employee]:
        pass

    def get_employees_by_department(self, department_id: int) -> list[Employee]:
        pass

    def add_employee(self, employee: Employee) -> int:
        pass

    def update_employee(self, employee: Employee) -> None:
        pass

    def delete_employee(self, employee_id: int) -> None:
        pass

    def delete_employees(self, company_id: int) -> None:
        pass
