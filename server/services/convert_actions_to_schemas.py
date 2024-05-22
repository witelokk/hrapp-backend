from typing import Iterator

from server.repo.departments_repository import DepartmentsRepository
from server.schemas.actions import (
    ActionWrapper,
    RecruitmentActionWrapper,
    PositionTransferActionWrapper,
    DepartmentTransferActionWrapper,
    SalaryChangeActionWrapper,
    DismissalActionWrapper,
    RecruitmentAction as RecruitmentActionSchema,
    PositionTransferAction as PositionTransferActionSchema,
    DepartmentTransferAction as DepartmentTransferActionSchema,
    SalaryChangeAction as SalaryChangeActionSchema,
    DismissalAction as DismissalActionSchema,
)
from server.schemas.departments import Department as DepartmentSchema
from server.model.action import *


def convert_actions_to_schemas(
    departments_repository: DepartmentsRepository, actions: list[Action]
) -> Iterator[ActionWrapper]:
    current_state = {"department": None, "position": None, "salary": None}

    for action in actions:
        if isinstance(action, RecruitmentAction):
            department = departments_repository.get_department(action.department_id)
            department = DepartmentSchema(
                id=department.id,
                name=department.name,
                company_id=department.company_id,
            )
            current_state = {
                "department": department,
                "position": action.position,
                "salary": action.salary,
            }
            yield RecruitmentActionWrapper(
                id=action.id,
                date=action.date,
                recruitment=RecruitmentActionSchema(
                    department=department,
                    position=action.position,
                    salary=action.salary,
                ),
            )

        elif isinstance(action, PositionTransferAction):
            yield PositionTransferActionWrapper(
                id=action.id,
                date=action.date,
                position_transfer=PositionTransferActionSchema(
                    previous_position=current_state["position"],
                    new_position=action.new_position,
                ),
            )
            current_state["position"] = action.new_position

        elif isinstance(action, DepartmentTransferAction):
            new_department = departments_repository.get_department(
                action.new_department_id
            )
            new_department = DepartmentSchema(
                id=new_department.id,
                name=new_department.name,
                company_id=new_department.company_id,
            )
            yield DepartmentTransferActionWrapper(
                id=action.id,
                date=action.date,
                department_transfer=DepartmentTransferActionSchema(
                    previous_department=current_state["department"],
                    new_department=new_department,
                ),
            )

            current_state["department"] = new_department

        elif isinstance(action, SalaryChangeAction):
            yield SalaryChangeActionWrapper(
                id=action.id,
                date=action.date,
                salary_change=SalaryChangeActionSchema(
                    previous_salary=current_state["salary"],
                    new_salary=action.new_salary,
                ),
            )
            current_state["salary"] = action.new_salary

        elif isinstance(action, DismissalAction):
            yield DismissalActionWrapper(
                id=action.id,
                date=action.date,
                dismissal=DismissalActionSchema(),
            )

    yield from []
