import datetime
from typing import Literal

from pydantic import BaseModel

from .departments import Department


class CreateRecruitmentActionRequest(BaseModel):
    action_type: Literal["recruitment"]
    date: datetime.date
    department_id: int
    position: str
    salary: float


class CreatePositionTransferActionRequest(BaseModel):
    action_type: Literal["position_transfer"]
    date: datetime.date
    new_position: str


class CreateDepartmentTransferActionRequest(BaseModel):
    action_type: Literal["department_transfer"]
    date: datetime.date
    new_department_id: int


class CreateSalaryChangeAction(BaseModel):
    action_type: Literal["salary_change"]
    date: datetime.date
    new_salary: float


class CreateDismissalAction(BaseModel):
    action_type: Literal["dismissal"]
    date: datetime.date


CreateActionRequest = (
    CreateRecruitmentActionRequest
    | CreatePositionTransferActionRequest
    | CreateDepartmentTransferActionRequest
    | CreateSalaryChangeAction
    | CreateDismissalAction
)


class RecruitmentAction(BaseModel):
    department: Department
    position: str
    salary: float


class PositionTransferAction(BaseModel):
    previous_position: str
    new_position: str


class DepartmentTransferAction(BaseModel):
    previous_department: Department
    new_department: Department


class SalaryChangeAction(BaseModel):
    previous_salary: float
    new_salary: float


class DismissalAction(BaseModel):
    pass


# class ActionWrapper(BaseModel):
#     action_type: Literal[
#         "recruitment",
#         "position_transfer",
#         "department_transfer",
#         "salary_change",
#         "dismissal",
#     ]
#     date: datetime.date
#     recruitment: RecruitmentAction | None = None
#     position_transfer: PositionTransferAction | None = None
#     department_transfer: DepartmentTransferAction | None = None
#     salary_change: SalaryChangeAction | None = None
#     dismissal: DismissalAction | None = None


class RecruitmentActionWrapper(BaseModel):
    action_type: Literal["recruitment"] = "recruitment"
    id: int
    date: datetime.date
    recruitment: RecruitmentAction


class PositionTransferActionWrapper(BaseModel):
    action_type: Literal["position_transfer"] = "position_transfer"
    id: int
    date: datetime.date
    position_transfer: PositionTransferAction


class DepartmentTransferActionWrapper(BaseModel):
    action_type: Literal["department_transfer"] = "department_transfer"
    id: int
    date: datetime.date
    department_transfer: DepartmentTransferAction


class SalaryChangeActionWrapper(BaseModel):
    action_type: Literal["salary_change"] = "salary_change"
    id: int
    date: datetime.date
    salary_change: SalaryChangeAction


class DismissalActionWrapper(BaseModel):
    action_type: Literal["dismissal"] = "dismissal"
    id: int
    date: datetime.date
    dismissal: DismissalAction


ActionWrapper = (
    RecruitmentActionWrapper
    | PositionTransferActionWrapper
    | DepartmentTransferActionWrapper
    | SalaryChangeActionWrapper
    | DismissalActionWrapper
)
