from dash import Dash
from opentelemetry import trace

from dash_extensions import enrich, plugins


class TracingPlugin(plugins.DashPlugin):
    def __init__(self, name: str = "tracing", app: Dash | None = None) -> None:
        super().__init__(name, app)
        self._tracer = trace.get_tracer(__name__)

    def plug(self, app: enrich.DashProxy) -> None:
        print(app)
        app.blueprint.transforms.append(TracingTransform())


class TracingTransform(enrich.DashTransform):
    def __init__(self):
        super().__init__()
        self.tracer = trace.get_tracer(__name__)

    def apply_serverside(self, callbacks):
        print(f"apply_serverside(callbacks={callbacks!r}")
        # Assuming callbacks is either a dict or a list; adjust as needed.
        if isinstance(callbacks, dict):
            return {key: self.wrap_callback(callback, key) for key, callback in callbacks.items()}
        elif isinstance(callbacks, list):
            return [
                self.wrap_callback(callback, getattr(callback, "__name__", "unknown_callback"))
                for callback in callbacks
            ]
        else:
            return self.wrap_callback(callbacks, getattr(callbacks, "__name__", "unknown_callback"))

    def wrap_callback(self, callback, callback_name):
        def wrapped_callback(*args, **kwargs):
            with self.tracer.start_as_current_span(f"callback: {callback_name}"):
                return callback(*args, **kwargs)

        return wrapped_callback

    def apply_clientside(self, callbacks):
        # Clientside callbacks run in the browser; leave them unmodified.
        print(f"apply_clientside(callbacks={callbacks!r}")
        return callbacks
