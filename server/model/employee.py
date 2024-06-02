from dataclasses import dataclass


@dataclass
class Employee:
    id: int
    owner_id: int
    name: str = None
    current_position: str = None
    current_salary: float = None
