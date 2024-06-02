from typing import Protocol

from server.model.department import Department


class DepartmentsRepository(Protocol):
    def get_department(self, department_id: int) -> Department:
        pass

    def get_departments(self, company_id: int) -> list[Department]:
        pass
