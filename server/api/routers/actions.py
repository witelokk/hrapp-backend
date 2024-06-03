from fastapi import HTTPException, status
from fastapi.routing import APIRouter

from server.schemas.actions import *
from server.api.dependenicies import user_dependency, actions_service_dependency
from server.database import models
from server.schemas.error import Error
from server.services.actions_service import (
    ActionNotExistsError,
    EmployeNotExistsError,
    ForbiddenError,
)

router = APIRouter(prefix="/actions", tags=["actions"])


# @router.get("/{action_id}")
# def get_action(db: db_dependency, user: user_dependency, action_id: int):
#     action = db.query(models.Action).filter_by(id=action_id).first()

#     if action is None:
#         raise HTTPException(status.HTTP_404_NOT_FOUND)

#     if action.employee.owner_id != user["id"]:
#         raise HTTPException(status.HTTP_403_FORBIDDEN)

#     return format_action(action)


@router.get(
    "/employee/{employee_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
    response_model_exclude_none=True,
)
def get_actions(
    actions_service: actions_service_dependency, user: user_dependency, employee_id: int
) -> list[ActionWrapper]:
    try:
        return actions_service.get_actions(user["id"], employee_id)
    except EmployeNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.post(
    "/employee/{employee_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def create_action(
    actions_service: actions_service_dependency,
    user: user_dependency,
    employee_id: int,
    create_action_request: CreateActionRequest,
) -> None:
    try:
        actions_service.create_action(
            user["id"], employee_id, create_action_request=create_action_request
        )
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.put(
    "/{action_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def edit_action(
    actions_service: actions_service_dependency,
    user: user_dependency,
    action_id: int,
    create_action_request: CreateActionRequest,
) -> None:
    try:
        actions_service.update_action(
            user["id"], action_id, create_action_request=create_action_request
        )
    except ActionNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Action does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


@router.delete(
    "/{action_id}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Error},
        status.HTTP_403_FORBIDDEN: {"model": Error},
        status.HTTP_401_UNAUTHORIZED: {"model": Error},
    },
)
def delete_action(
    actions_service: actions_service_dependency, user: user_dependency, action_id: int
):
    try:
        actions_service.delete_action(user["id"], action_id)
    except ActionNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Action does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
