from dataclasses import dataclass
from datetime import date


@dataclass
class Action:
    employee_id: int
    date: date


@dataclass
class RecruitmentAction(Action):
    department_id: int
    position: str
    salary: float
    id: int = None


@dataclass
class PositionTransferAction(Action):
    new_position: str
    id: int = None


@dataclass
class DepartmentTransferAction(Action):
    new_department_id: int
    id: int = None


@dataclass
class SalaryChangeAction(Action):
    new_salary: float
    id: int = None


@dataclass
class DismissalAction(Action):
    id: int = None
