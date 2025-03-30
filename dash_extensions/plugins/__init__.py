__all__ = ["DashPlugin", "PluginRegistry"]

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


class PluginRegistry(dict):
    # TODO: Do we need to support any sort of finalization after "plug"

    def __init__(self, *plugins: DashPlugin):
        plugin_names = list(plugin.name for plugin in plugins)
        if len(plugin_names) != len(set(plugin_names)):
            raise ValueError("Plugins must have unique names")
        super().__init__({plugin.name: plugin for plugin in plugins})

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
            raise AttributeError(f"No such plugin named {item!r}")

    def __setattr__(self, key: str, val: DashPlugin) -> None:
        return super().__setitem__(key, val)

    def __setitem__(self, key: str, val: DashPlugin) -> None:
        return super().__setitem__(key, val)

    def attach(self, app: Dash) -> "PluginRegistry":
        existing_registry: PluginRegistry | None = getattr(app, "plugins")

        if existing_registry is not None:
            # TODO: Should we check for name conflicts? If attaching, do we mind?
            existing_registry.update(self)
        else:
            app.plugins = self

        return app.plugins


def _attach_app_plugin(app: Dash, plugin: DashPlugin) -> None:
    plugins_registry = _get_plugins_registry(app)
    existing_plugin = getattr(plugins_registry, plugin.name, None)

    if existing_plugin:
        raise RuntimeError(f"Plugin name collision: {existing_plugin} and {plugin}")

    setattr(plugins_registry, plugin.name, plugin)


def _get_plugins_registry(app: Dash):
    return attr_setdefault(app, "plugins", PluginRegistry)
