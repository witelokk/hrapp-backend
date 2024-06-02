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

    def get_employees(self, department_id: int) -> list[Employee]:
        db_employees = self._db.query(DbEmployee).all()
        return [
            Employee(
                db_employee.id,
                db_employee.owner_id,
                db_employee.name,
                db_employee.current_position,
                db_employee.current_salary,
            )
            for db_employee in db_employees
            if db_employee.current_department
            and db_employee.current_department.id == department_id
        ]

    def delete_employees(self, company_id: int) -> None:
        employees = [
            employee
            for employee in self._db.query(DbEmployee).all()
            if employee.current_company and employee.current_company.id == company_id
        ]

        for employee in employees:
            self._db.delete(employee)

        self._db.commit()
