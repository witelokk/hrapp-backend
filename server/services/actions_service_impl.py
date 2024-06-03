from server.repo.actions_repository import ActionsRepository
from server.repo.departments_repository import DepartmentsRepository
from server.repo.employees_repository import EmployeesRepository
from server.services.convert_actions_to_schemas import convert_actions_to_schemas
from .actions_service import (
    ActionNotExistsError,
    ActionsService,
    EmployeNotExistsError,
    ForbiddenError,
    DepartmentNotExistsError,
    NoAccessToDepartmentError,
)
from server.schemas.actions import CreateActionRequest
from server.model.action import *


class ActionsServiceImpl(ActionsService):
    def __init__(
        self,
        actions_repository: ActionsRepository,
        employees_repository: EmployeesRepository,
        departments_repository: DepartmentsRepository,
    ):
        self._actions_repository = actions_repository
        self._employees_repository = employees_repository
        self._departments_repository = departments_repository

    def get_actions(self, user_id: int, employee_id: int):
        employee = self._employees_repository.get_employee(employee_id)

        if employee is None:
            raise EmployeNotExistsError()

        if employee.owner_id != user_id:
            raise ForbiddenError()

        actions = self._actions_repository.get_actions(employee_id)

        return list(convert_actions_to_schemas(self._departments_repository, actions))

    def get_action(self, user_id: int, action_id: int):
        raise NotImplementedError()

    def create_action(
        self, user_id: int, employee_id: int, create_action_request: CreateActionRequest
    ):
        employee = self._employees_repository.get_employee(employee_id)

        if employee.owner_id != user_id:
            raise ForbiddenError()

        action = self._create_action_from_request(
            user_id, employee_id, create_action_request
        )
        self._actions_repository.add_action(action)

    def update_action(
        self, user_id: int, action_id: int, create_action_request: CreateActionRequest
    ):
        action = self._actions_repository.get_action(action_id)

        if not action:
            raise ActionNotExistsError()

        employee = self._employees_repository.get_employee(action.employee_id)

        if employee.owner_id != user_id:
            raise ForbiddenError()

        new_action = self._create_action_from_request(
            user_id, action.employee_id, create_action_request
        )
        new_action.id = action.id

        self._actions_repository.update_action(new_action)

    def delete_action(self, user_id: int, action_id: int):
        action = self._actions_repository.get_action(action_id)

        if not action:
            raise ActionNotExistsError()

        employee = self._employees_repository.get_employee(action.employee_id)

        if employee.owner_id != user_id:
            raise ForbiddenError()

        self._actions_repository.delete_action(action_id=action_id)

    def _create_action_from_request(
        self, user_id: int, employee_id: int, create_action_request: CreateActionRequest
    ) -> Action:
        match create_action_request.action_type:
            case "recruitment":
                department = self._departments_repository.get_department(
                    create_action_request.department_id
                )

                if department is None:
                    raise DepartmentNotExistsError()

                if department.owner_id != user_id:
                    raise NoAccessToDepartmentError()

                return RecruitmentAction(
                    employee_id=employee_id,
                    date=create_action_request.date,
                    department_id=create_action_request.department_id,
                    position=create_action_request.position,
                    salary=create_action_request.salary,
                )
            case "position_transfer":
                return PositionTransferAction(
                    employee_id=employee_id,
                    date=create_action_request.date,
                    new_position=create_action_request.new_position,
                )
            case "department_transfer":
                department = self._departments_repository.get_department(
                    create_action_request.new_department_id
                )

                if department is None:
                    raise DepartmentNotExistsError()

                if department.owner_id != user_id:
                    raise NoAccessToDepartmentError()

                return DepartmentTransferAction(
                    employee_id=employee_id,
                    date=create_action_request.date,
                    new_department_id=create_action_request.new_department_id,
                )
            case "salary_change":
                return SalaryChangeAction(
                    employee_id=employee_id,
                    date=create_action_request.date,
                    new_salary=create_action_request.new_salary,
                )
            case "dismissal":
                return DismissalAction(
                    employee_id=employee_id,
                    date=create_action_request.date,
                )
