from sqlalchemy.orm import Session

from server.model.employee import Employee
from server.model.department import Department
from server.database.models import Employee as DbEmployee
from .employees_repository import EmployeesRepository


def employee_from_db(db_employee: DbEmployee) -> Employee:
    return Employee(
        id=db_employee.id,
        owner_id=db_employee.owner_id,
        name=db_employee.name,
        gender=db_employee.gender.name,
        birthdate=db_employee.birthdate,
        inn=db_employee.inn,
        snils=db_employee.snils,
        address=db_employee.address,
        passport_number=db_employee.passport_number,
        passport_date=db_employee.passport_date,
        passport_issuer=db_employee.passport_issuer,
        current_position=db_employee.current_position,
        current_department=(
            Department(
                id=db_employee.current_department.id,
                owner_id=db_employee.current_department.company.owner_id,
                name=db_employee.current_department.name,
                company_id=db_employee.current_department.company_id,
            )
            if db_employee.current_department
            else None
        ),
        current_salary=db_employee.current_salary,
        last_company_id=db_employee.last_copmany.id if db_employee.last_copmany else None
    )


def db_from_employee(employee: Employee) -> DbEmployee:
    return DbEmployee(
        id=employee.id,
        owner_id=employee.owner_id,
        name=employee.name,
        gender=employee.gender,
        birthdate=employee.birthdate,
        inn=employee.inn,
        snils=employee.snils,
        address=employee.address,
        passport_number=employee.passport_number,
        passport_date=employee.passport_date,
        passport_issuer=employee.passport_issuer,
    )


class EmployeesRepositoryImpl(EmployeesRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_employee(self, employee_id: int) -> Employee:
        db_employee = self._db.query(DbEmployee).filter_by(id=employee_id).one_or_none()

        if db_employee is None:
            return None

        return employee_from_db(db_employee)

    def get_employees_by_company(self, company_id: int) -> list[Employee]:
        db_employees = self._db.query(DbEmployee).all()
        return [
            employee_from_db(db_employee)
            for db_employee in db_employees
            if db_employee.last_copmany and db_employee.last_copmany.id == company_id
        ]

    def get_employees_by_department(self, department_id: int) -> list[Employee]:
        db_employees = self._db.query(DbEmployee).all()
        return [
            employee_from_db(db_employee)
            for db_employee in db_employees
            if db_employee.current_department
            and db_employee.current_department.id == department_id
        ]

    def add_employee(self, employee: Employee) -> int:
        db_employee = db_from_employee(employee)
        self._db.add(db_employee)
        self._db.commit()
        return db_employee.id

    def update_employee(self, employee: Employee) -> None:
        db_employee = self._db.query(DbEmployee).filter_by(id=employee.id).one_or_none()
        db_employee.owner_id = employee.owner_id
        db_employee.name = employee.name
        db_employee.gender = employee.gender
        db_employee.birthdate = employee.birthdate
        db_employee.inn = employee.inn
        db_employee.snils = employee.snils
        db_employee.address = employee.address
        db_employee.passport_number = employee.passport_number
        db_employee.passport_date = employee.passport_date
        db_employee.passport_issuer = employee.passport_issuer
        self._db.commit()

    def delete_employee(self, employee_id: int) -> None:
        employee = self._db.query(DbEmployee).filter_by(id=employee_id).one_or_none()

        if employee is None:
            return

        self._db.delete(employee)
        self._db.commit()

    def delete_employees(self, company_id: int) -> None:
        employees = [
            employee
            for employee in self._db.query(DbEmployee).all()
            if employee.current_company and employee.current_company.id == company_id
        ]

        for employee in employees:
            self._db.delete(employee)

        self._db.commit()
