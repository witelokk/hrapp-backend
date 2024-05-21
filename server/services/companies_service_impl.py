from typing import Iterable

from server.model.company import Company
from server.repo.companies_repository import CompaniesRepository
from .companies_service import CompaniesService, CompanyNotExistError, ForbiddenError


class CompaniesServiceImpl(CompaniesService):
    def __init__(self, companies_repository: CompaniesRepository):
        self._repository = companies_repository

    def get_companies(self, user_id: int) -> Iterable[Company]:
        return self._repository.get_companies(user_id)

    def get_company(self, user_id: int, company_id: int) -> Company:
        company = self._repository.get_company(company_id)

        if not company:
            raise CompanyNotExistError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        return company

    def create_company(
        self,
        name: str,
        inn: str,
        kpp: str,
        owner_id: int,
    ) -> int:
        self._repository.create_company(name, inn, kpp, owner_id)

    def edit_company(
        self,
        user_id: int,
        company_id: int,
        *,
        name: str = None,
        inn: str = None,
        kpp: str = None,
        owner_id: int = None,
    ) -> None:
        company = self._repository.get_company(company_id)

        if company is None:
            raise CompanyNotExistError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        self._repository.edit_company(
            company_id, name=name, inn=inn, kpp=kpp, owner_id=owner_id
        )

    def delete_company(self, user_id: int, company_id: int) -> None:
        company = self._repository.get_company(company_id)

        if company is None:
            raise CompanyNotExistError()

        if company.owner_id != user_id:
            raise ForbiddenError()

        self._repository.delete_company(company_id)
