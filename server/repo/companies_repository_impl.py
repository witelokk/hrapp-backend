from typing import Iterable

from sqlalchemy.orm import Session

from server.model.company import Company
from server.database.models import Company as DbCompany
from .companies_repository import CompaniesRepository


class CompaniesRepositoryImpl(CompaniesRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_companies(self, user_id: int) -> Iterable[Company]:
        db_companies = self._db.query(DbCompany).filter_by(owner_id=user_id).all()

        return [
            Company(
                id=db_company.id,
                name=db_company.name,
                inn=db_company.inn,
                kpp=db_company.kpp,
                owner_id=db_company.owner_id,
            )
            for db_company in db_companies
        ]

    def get_company(self, company_id: int) -> Company:
        db_company = self._db.query(DbCompany).filter_by(id=company_id).one_or_none()
        return Company(
            id=db_company.id,
            name=db_company.name,
            inn=db_company.inn,
            kpp=db_company.kpp,
            owner_id=db_company.owner_id,
        )

    def create_company(
        self,
        name: str,
        inn: str,
        kpp: str,
        owner_id: int,
    ) -> int:
        db_company = DbCompany(name=name, inn=inn, kpp=kpp, owner_id=owner_id)
        self._db.add(db_company)
        self._db.commit()
        return db_company.id

    def edit_company(
        self,
        company_id: int,
        *,
        name: str = None,
        inn: str = None,
        kpp: str = None,
        owner_id: int = None,
    ) -> None:
        db_company = self._db.query(DbCompany).filter_by(id=company_id).one_or_none()

        if name:
            db_company.name = name
        if inn:
            db_company.inn = inn
        if kpp:
            db_company.kpp = kpp
        if owner_id:
            db_company.owner_id = owner_id

        self._db.commit()

    def delete_company(self, company_id: int) -> None:
        db_company = self._db.query(DbCompany).filter_by(id=company_id).delete()
