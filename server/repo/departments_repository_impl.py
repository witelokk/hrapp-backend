from sqlalchemy.orm import Session

from server.model.department import Department
from server.database.models import Department as DbDepartment
from .departments_repository import DepartmentsRepository


class DepartmentsRepositoryImpl(DepartmentsRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_department(self, department_id: int) -> Department:
        db_department = (
            self._db.query(DbDepartment).filter_by(id=department_id).one_or_none()
        )
        return Department(
            id=db_department.id,
            name=db_department.name,
            company_id=db_department.company_id,
        )

    def get_departments(self, company_id: int) -> list[Department]:
        db_departments = (
            self._db.query(DbDepartment).filter_by(company_id=company_id).all()
        )
        return [
            Department(
                id=db_department.id,
                name=db_department.name,
                company_id=db_department.company_id,
            )
            for db_department in db_departments
        ]
