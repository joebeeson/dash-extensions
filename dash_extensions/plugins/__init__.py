__all__ = ["DashPlugin", "PluginRegistry"]

from typing import Iterator

from dash import Dash

from dash_extensions.utils import attr_setdefault
from dash_extensions.plugins.errors import PluginMissing, PluginNameConflict


class DashPlugin:
    # TODO: How can we add our own transforms to the application?

    def __init__(self, name: str, app: Dash | None = None):
        self.name = name
        self.app = app

        if app is not None:
            self.plug(app)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"

    def plug(self, app: Dash) -> None:
        """Interface for `dash.Dash:__init__` to add the plugin."""
        _attach_app_plugin(app, self)
        self.app = app

    def init_app(self) -> None:
        """Callback triggered on application initialization, before startup."""
        pass

    def setup_server(self) -> None:
        """Callback triggered on application startup, after initialization."""
        pass


class PluginRegistry(dict):
    # TODO: Do we need to support any sort of finalization after "plug"

    def __init__(self, *plugins: DashPlugin, app: Dash | None = None):
        plugin_names = list(plugin.name for plugin in plugins)

        if len(plugin_names) != len(set(plugin_names)):
            raise PluginNameConflict()

        super().__init__({plugin.name: plugin for plugin in plugins})

        if app is not None:
            self.plug(app)

    def __repr__(self) -> str:
        plugins = " ".join(repr(plugin) for plugin in self)
        return f"{self.__class__.__name__}({plugins})"

    def plug(self, app: Dash) -> None:
        """Enjoin the registered plugins to the application."""
        for plugin in self.attach(app):
            plugin.plug(app)

    def __iter__(self) -> Iterator[DashPlugin]:
        """Support use directly as the `plugins` argument: iterate the plugins."""
        return iter(self.values())

    def __getattr__(self, item: str) -> DashPlugin:
        """Allow attribute access to the plugins by name (key)"""
        try:
            return self[item]
        except KeyError:
            raise PluginMissing(item)

    def __setattr__(self, key: str, val: DashPlugin) -> None:
        return super().__setitem__(key, val)

    def __setitem__(self, key: str, val: DashPlugin) -> None:
        return super().__setitem__(key, val)

    def attach(self, app: Dash) -> "PluginRegistry":
        existing_registry = getattr(app, "plugins")

        if existing_registry is not None:
            #: Other registry here?? TODO: Do we need to check for collisions?
            existing_registry.update(self)
        else:
            #: We're attaching our instance; wrap the `init_app` for our plugins:
            app.init_app = lambda *args, **kwargs: self.init_app(*args, **kwargs)
            app.plugins = self

        return app.plugins

    def init_app(self, app=None, **kwargs):
        for plugin in self:
            plugin.init_app()


def _attach_app_plugin(app: Dash, plugin: DashPlugin) -> None:
    """Attach the plugin to the application, possibly creating the registry."""
    plugins_registry = _get_plugins_registry(app)

    if getattr(plugins_registry, plugin.name, plugin) != plugin:
        raise PluginNameConflict()

    # TODO: Do we need a lock for mutating the registry?
    setattr(plugins_registry, plugin.name, plugin)


def _get_plugins_registry(app: Dash | None = None):
    # TODO: Do we need a lock for mutating the application?
    return attr_setdefault(app, "plugins", PluginRegistry(app=app))
