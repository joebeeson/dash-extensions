__all__ = ["RequestLoader", "UserLoader", "UserMixin"]
from typing import Callable, TypeVar

import flask
import flask_login



RequestLoader = Callable[[flask.Request], "UserMixin"]

UserLoader = Callable[[str], "UserMixin"]

UserMixin = TypeVar("UserMixin", bound=flask_login.UserMixin)
