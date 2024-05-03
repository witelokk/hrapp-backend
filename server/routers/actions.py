import datetime
from typing import Annotated, Literal
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from pydantic import BaseModel, RootModel, Discriminator

from . import auth

from .. import models
from ..database import db_dependency

router = APIRouter(prefix="/actions", tags=["actions"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class CreateRecruitmentActionRequest(BaseModel):
    action_type: Literal["recruitment"]
    recruitment_date: datetime.date
    department_id: int
    position: str
    salary: float


class CreatePositionTransferActionRequest(BaseModel):
    action_type: Literal["position_transfer"]
    transfer_date: datetime.date
    new_position: str


class CreateDepartmentTransferActionRequest(BaseModel):
    action_type: Literal["department_transfer"]
    transfer_date: datetime.date
    new_department_id: int


class CreateSalaryChangeAction(BaseModel):
    action_type: Literal["salary_change"]
    change_date: datetime.date
    new_salary: float


class CreateDissmissalAction(BaseModel):
    action_type: Literal["dismissal"]
    dismissal_date: datetime.date


CreateActionRequest = (
    CreateRecruitmentActionRequest
    | CreatePositionTransferActionRequest
    | CreateDepartmentTransferActionRequest
    | CreateSalaryChangeAction
    | CreateDissmissalAction
)


def format_action(action: models.Action):
    res = {
        "id": action.id,
        "action_type": action.action_type,
    }

    if action.action_type == "recruitment":
        res.update(
            {
                "department_id": action.department_id,
                "recruitment_date": action.recruitment_date,
                "position": action.position,
                "salary": action.salary,
            }
        )
    elif action.action_type == "position_transfer":
        res.update(
            {"transfer_date": action.transfer_date, "new_position": action.new_position}
        )
    elif action.action_type == "department_transfer":
        res.update(
            {
                "transfer_date": action.transfer_date,
                "new_department_id": action.new_department_id,
            }
        )
    elif action.action_type == "salary_change":
        res.update({"change_date": action.change_date, "new_salary": action.new_salary})
    elif action.action_type == "dismissal":
        res.update({"dismissal_date": action.dismissal_date})

    return res


@router.get("/employee/{employee_id}")
def get_actions(db: db_dependency, user: user_dependency, employee_id: int) -> list:
    employee = db.query(models.Employee).filter_by(id=employee_id).first()

    if not employee.company.owner_id == user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No access to the user")

    actions = db.query(models.Action).filter_by(employee=employee).all()

    return [format_action(a) for a in actions]


@router.post("/employee/{employee_id}", status_code=status.HTTP_201_CREATED)
def create_action(
    db: db_dependency,
    user: user_dependency,
    employee_id: int,
    create_action_request: CreateActionRequest,
):
    employee = db.query(models.Employee).filter_by(id=employee_id).first()

    if not employee.company.owner_id == user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    if create_action_request.action_type == "recruitment":
        department = (
            db.query(models.Department)
            .filter_by(id=create_action_request.department_id)
            .first()
        )

        if not department:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Department does not exist"
            )

        if department.company.owner_id != user["id"]:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        action = models.RecruitmentAction(
            employee=employee,
            department=department,
            recruitment_date=create_action_request.recruitment_date,
            position=create_action_request.position,
            salary=create_action_request.salary,
        )
        db.add(action)
    elif create_action_request.action_type == "position_transfer":
        action = models.PositionTransferAction(
            employee=employee,
            transfer_date=create_action_request.transfer_date,
            new_position=create_action_request.new_position,
        )
        db.add(action)
    elif create_action_request.action_type == "department_transfer":
        department = (
            db.query(models.Department)
            .filter_by(id=create_action_request.new_department_id)
            .first()
        )

        if not department:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Department does not exist"
            )

        if department.company.owner_id != user["id"]:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        action = models.DepartmentTransferAction(
            employee=employee,
            transfer_date=create_action_request.transfer_date,
            new_department_id=create_action_request.new_department_id,
        )
        db.add(action)
    elif create_action_request.action_type == "salary_change":
        action = models.SalaryChangeAction(
            employee=employee,
            new_salary=create_action_request.new_salary,
            change_date=create_action_request.change_date,
        )
        db.add(action)
        db.commit()
    elif create_action_request.action_type == "dismissal":
        action = models.DissmisalAction(
            employee=employee,
            dismissal_date=create_action_request.dismissal_date,
        )
        db.add(action)

    db.commit()
