from dataclasses import dataclass


@dataclass
class Department:
    id: int
    name: str
    company_id: int
