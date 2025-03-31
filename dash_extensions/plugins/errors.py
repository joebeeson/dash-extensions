class PluginMissing(Exception):
    """Exception raised when a requested plugin (name) isn't defined."""

    pass


class PluginNameConflict(Exception):
    """Exception raised when a plugin name conflicts."""

    pass
