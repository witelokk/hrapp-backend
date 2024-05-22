from typing import Protocol

from server.model.employee import Employee


class EmployeesRepository(Protocol):
    def get_employee(self, employee_id: int) -> Employee:
        pass
