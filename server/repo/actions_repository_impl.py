from typing import Iterable

from sqlalchemy.orm import Session

from server.model.action import *
from server.database.models import (
    Action as DbAction,
    RecruitmentAction as DbRecruitmentAction,
    PositionTransferAction as DbPositionTransferAction,
    DepartmentTransferAction as DbDepartmentTransferAction,
    SalaryChangeAction as DbSalaryChangeAction,
    DismissalAction as DbDismissalAction,
)
from .actions_repository import ActionsRepository


def db_action_to_action(db_action: DbAction) -> Action:
    if db_action.action_type == "recruitment":
        return RecruitmentAction(
            employee_id=db_action.employee_id,
            id=db_action.id,
            department_id=db_action.department_id,
            date=db_action.date,
            position=db_action.position,
            salary=db_action.salary,
        )
    if db_action.action_type == "position_transfer":
        return PositionTransferAction(
            employee_id=db_action.employee_id,
            id=db_action.id,
            date=db_action.date,
            new_position=db_action.new_position,
        )
    if db_action.action_type == "department_transfer":
        return DepartmentTransferAction(
            employee_id=db_action.employee_id,
            id=db_action.id,
            date=db_action.date,
            new_department_id=db_action.new_department_id,
        )
    if db_action.action_type == "salary_change":
        return SalaryChangeAction(
            employee_id=db_action.employee_id,
            id=db_action.id,
            date=db_action.date,
            new_salary=db_action.new_salary,
        )
    if db_action.action_type == "dismissal":
        return DismissalAction(
            employee_id=db_action.employee_id,
            id=db_action.id,
            date=db_action.date,
        )


def action_to_db_action(action: Action) -> DbAction:
    if isinstance(action, RecruitmentAction):
        return DbRecruitmentAction(
            employee_id=action.employee_id,
            id=action.id,
            department_id=action.department_id,
            date=action.date,
            position=action.position,
            salary=action.salary,
        )
    if isinstance(action, PositionTransferAction):
        return DbPositionTransferAction(
            employee_id=action.employee_id,
            id=action.id,
            date=action.date,
            new_position=action.new_position,
        )
    if isinstance(action, DepartmentTransferAction):
        return DbDepartmentTransferAction(
            employee_id=action.employee_id,
            id=action.id,
            date=action.date,
            new_department_id=action.new_department_id,
        )
    if isinstance(action, SalaryChangeAction):
        return DbSalaryChangeAction(
            employee_id=action.employee_id,
            id=action.id,
            date=action.date,
            new_salary=action.new_salary,
        )
    if isinstance(action, DismissalAction):
        return DbDismissalAction(
            employee_id=action.employee_id,
            id=action.id,
            date=action.date,
        )


class ActionsRepositoryImpl(ActionsRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_actions(self, employee_id: int) -> Iterable[Action]:
        db_actions = (
            self._db.query(DbAction)
            .filter_by(employee_id=employee_id)
            .order_by(DbAction.date)
            .all()
        )
        return [db_action_to_action(db_action) for db_action in db_actions]

    def get_action(self, action_id: int) -> Action:
        db_action = self._db.query(DbAction).filter_by(id=action_id).one_or_none()
        return db_action_to_action(db_action)

    def add_action(self, action: Action):
        db_action = action_to_db_action(action)
        self._db.add(db_action)
        self._db.commit()

    def update_action(self, new_action: Action):
        self._db.query(DbAction).filter_by(id=new_action.id).delete()
        db_action = action_to_db_action(new_action)
        self._db.add(db_action)
        self._db.commit()

    def delete_action(self, action_id: int):
        self._db.query(DbAction).filter_by(id=action_id).delete()
        self._db.commit()
