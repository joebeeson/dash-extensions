from typing import Iterator

from dash import Dash


class DashPlugin:
    def plug(self, app: Dash) -> None:
        pass


class Registry:
    def __init__(self, **plugins: DashPlugin):
        self.plugins = plugins

    def plug(self, app: Dash) -> None:
        for plugin in self:
            plugin.plug(app)

    def __iter__(self) -> Iterator[DashPlugin]:
        return iter(self.plugins.values())

    def __getattr__(self, item) -> DashPlugin:
        try:
            return self.plugins[item]
        except KeyError:
            raise AttributeError(f"No such plugin named {item!r}")

