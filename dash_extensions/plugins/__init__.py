__all__ = ["DashPlugin", "Registry"]

from typing import Iterator

from dash import Dash

from dash_extensions.utils import attr_setdefault


class DashPlugin:
    def __init__(self, name: str, app: Dash | None = None):
        self.name = name
        self.app = app

        if app is not None:
            self.plug(app)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, app={self.app!r})"

    def plug(self, app: Dash) -> None:
        _attach_app_plugin(app, self)
        self.app = app


class Registry(dict):
    # TODO: Need to be able to close the registry at startup ala AttributeDict

    def __init__(self, *plugins: DashPlugin):
        plugin_names = list(plugin.name for plugin in plugins)
        if len(plugin_names) != len(set(plugin_names)):
            raise ValueError("Plugins must have unique names")
        super().__init__({plugin.name: plugin for plugin in plugins})

    def plug(self, app: Dash) -> None:
        for plugin in self.attach(app):
            plugin.plug(app)

    def __iter__(self) -> Iterator[DashPlugin]:
        return iter(self.values())

    def __getattr__(self, item) -> DashPlugin:
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"No such plugin named {item!r}")

    def __setattr__(self, key, val):
        return super().__setitem__(key, val)

    def __setitem__(self, key, val):
        return super().__setitem__(key, val)

    def attach(self, app: Dash) -> "Registry":
        existing_registry: Registry | None = getattr(app, "plugins")

        if existing_registry is not None:
            # TODO: Check for duplicates (name):
            existing_registry.update(self)
        else:
            app.plugins = self

        return self


def _attach_app_plugin(app: Dash, plugin: DashPlugin) -> None:
    plugins = attr_setdefault(app, "plugins", Registry())
    plugin_name = plugin.name
    existing_plugin = getattr(plugins, plugin_name, None)

    if existing_plugin:
        raise RuntimeError(f"Plugin name collision: {existing_plugin} and {plugin}")

    setattr(plugins, plugin.name, plugin)
