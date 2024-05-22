from sqlalchemy.orm import Session

from server.model.employee import Employee
from server.database.models import Employee as DbEmployee
from .employees_repository import EmployeesRepository


class EmployeesRepositoryImpl(EmployeesRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_employee(self, employee_id: int):
        db_employee = self._db.query(DbEmployee).filter_by(id=employee_id).one_or_none()
        return Employee(db_employee.id, db_employee.owner_id)
