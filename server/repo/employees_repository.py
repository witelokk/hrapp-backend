from typing import Protocol

from server.model.employee import Employee


class EmployeesRepository(Protocol):
    def get_employee(self, employee_id: int) -> Employee:
        pass

    def get_employees(self, department_id: int) -> list[Employee]:
        pass

    def delete_employees(self, company_id: int) -> None:
        pass
