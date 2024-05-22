from dataclasses import dataclass


@dataclass
class Employee:
    id: int
    owner_id: int
