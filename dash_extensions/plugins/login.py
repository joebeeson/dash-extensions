__all__ = ["LoginPlugin"]
from typing import Generic

from . import Dash, DashPlugin

from flask_login import LoginManager

from ._typing import RequestLoader, UserLoader, UserMixin



class LoginPlugin(DashPlugin, Generic[UserMixin]):
    def __init__(self, name: str = "login", app: Dash | None = None):
        super().__init__(name, app)
        self._login_manager = LoginManager()

    def request_loader(self, callback: RequestLoader) -> RequestLoader:
        self._login_manager.request_loader(callback)
        return callback

    def user_loader(self, callback: UserLoader) -> UserLoader:
        self._login_manager.user_loader(callback)
        return callback

