__all__ = [
    "DashPlugin",
    "Registry"
]
from typing import Iterator

from dash import Dash


class DashPlugin:
    def __init__(self, name: str, app: Dash | None = None):
        self.name = name
        self.app = app
        print(f"Created {self}")

        if app is not None:
            self.plug(app)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, app={self.app!r})"

    def plug(self, app: Dash) -> None:
        self.app = app
        print(f"Plugged {self}")
        return
        self.config = AttributeDict(
            name=name,
            assets_folder=os.path.join(
                flask.helpers.get_root_path(name), assets_folder
            ),  # type: ignore
            assets_url_path=assets_url_path,
            assets_ignore=assets_ignore,
            assets_external_path=get_combined_config(
                "assets_external_path", assets_external_path, ""
            ),
            pages_folder=pages_folder_config(name, pages_folder, use_pages),
            eager_loading=eager_loading,
            include_assets_files=get_combined_config(
                "include_assets_files", include_assets_files, True
            ),
            url_base_pathname=base_prefix,
            routes_pathname_prefix=routes_prefix,
            requests_pathname_prefix=requests_prefix,
            serve_locally=serve_locally,
            compress=get_combined_config("compress", compress, False),
            meta_tags=meta_tags or [],
            external_scripts=external_scripts or [],
            external_stylesheets=external_stylesheets or [],
            suppress_callback_exceptions=get_combined_config(
                "suppress_callback_exceptions", suppress_callback_exceptions, False
            ),
            prevent_initial_callbacks=prevent_initial_callbacks,
            show_undo_redo=show_undo_redo,
            extra_hot_reload_paths=extra_hot_reload_paths or [],
            title=title,
            update_title=update_title,
            include_pages_meta=include_pages_meta,
            description=description,
        )
        self.config.set_read_only(
            [
                "name",
                "assets_folder",
                "assets_url_path",
                "eager_loading",
                "serve_locally",
                "compress",
                "pages_folder",
            ],
            "Read-only: can only be set in the Dash constructor",
        )
        self.config.finalize(
            "Invalid config key. Some settings are only available "
            "via the Dash constructor"
        )
        pass


class Registry(dict):
    def __init__(self, *plugins: DashPlugin):
        super().__init__({plugin.name: plugin for plugin in plugins})

    def plug(self, app: Dash) -> None:
        for plugin in self:
            plugin.plug(app)

    def __iter__(self) -> Iterator[DashPlugin]:
        return iter(self.values())

    def __getattr__(self, item) -> DashPlugin:
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"No such plugin named {item!r}")

