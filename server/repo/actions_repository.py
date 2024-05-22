from typing import Iterable, Protocol

from server.model.action import *


class ActionsRepository(Protocol):
    def get_actions(self, employee_id: int) -> Iterable[Action]:
        pass

    def get_action(self, action_id: int) -> Action:
        pass

    def add_action(self, action: Action):
        pass

    def update_action(self, new_action: Action):
        pass

    def delete_action(self, action_id: int):
        pass
