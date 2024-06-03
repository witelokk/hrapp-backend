from typing import Protocol

from server.schemas.actions import CreateActionRequest, ActionWrapper


class ActionNotExistsError(Exception):
    pass


class EmployeNotExistsError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class DepartmentNotExistsError(Exception):
    pass


class NoAccessToDepartmentError(Exception):
    pass


class ActionsService(Protocol):
    def get_actions(self, user_id: int, employee_id: int) -> list[ActionWrapper]:
        pass

    def get_action(self, user_id: int, action_id: int) -> ActionWrapper:
        pass

    def create_action(
        self, user_id: int, employee_id: int, create_action_request: CreateActionRequest
    ):
        pass

    def update_action(
        self, user_id: int, action_id: int, create_action_request: CreateActionRequest
    ):
        pass

    def delete_action(self, user_id: int, action_id: int) -> None:
        pass
