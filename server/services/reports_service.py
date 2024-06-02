from typing import Protocol


class ForbiddenError(Exception):
    pass


class CompanyNotExistsError(Exception):
    pass


class ReportsService(Protocol):
    def generate_report(self, user_id: int, company_id: int) -> bytes:
        pass
