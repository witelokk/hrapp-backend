from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    name: str
    inn: str
    kpp: str
    owner_id: int
    id: int = None
