from typing import Iterable, Protocol

from server.model.company import Company


class CompaniesRepository(Protocol):
    def get_companies(self, user_id: int) -> Iterable[Company]:
        pass

    def get_company(self, company_id: int) -> Company:
        pass

    def create_company(
        self,
        name: str,
        inn: str,
        kpp: str,
        owner_id: int,
    ) -> int:
        pass

    def edit_company(
        self,
        company_id: int,
        *,
        name: str = None,
        inn: str = None,
        kpp: str = None,
        owner_id: int = None,
    ) -> None:
        pass

    def delete_company(self, company_id: int) -> None:
        pass
