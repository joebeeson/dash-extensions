import pytest

from dash_extensions.plugins import DashPlugin, PluginRegistry
from dash import Dash


# Test that creating a Registry with unique plugin names works as expected


def test_registry_unique_names():
    # Create plugins without attaching them to any app
    plugin1 = DashPlugin("unique1")
    plugin2 = DashPlugin("unique2")
    # Creating the registry should not raise an error
    registry = PluginRegistry(plugin1, plugin2)

    # Verify that the registry contains the correct plugins
    assert registry["unique1"] is plugin1
    assert registry["unique2"] is plugin2


# Test that creating a Registry with duplicate plugin names raises a ValueError


def test_registry_duplicate_names():
    plugin1 = DashPlugin("dupe")
    plugin2 = DashPlugin("dupe")
    with pytest.raises(ValueError, match="Plugins must have unique names"):
        PluginRegistry(plugin1, plugin2)


# Test that attempting to attach a plugin to a Dash app when a plugin with the
# same name has already been attached raises a RuntimeError for plugin collision


def test_plugin_collision():
    # Create a Dash app instance
    app = Dash("TestApp")

    # Attach a plugin to the app; __init__ with app automatically plugs it
    plugin1 = DashPlugin("collision_plugin", app=app)

    # Create a second plugin with the same name, but do not attach it at creation
    plugin2 = DashPlugin("collision_plugin")

    # Attempting to plug the second plugin into the same app should trigger a collision
    with pytest.raises(RuntimeError, match="Plugin name collision"):
        plugin2.plug(app)


if __name__ == "__main__":
    pytest.main([__file__])
