from dash import Dash
from opentelemetry import trace

from dash_extensions.enrich import DashTransform
from plugins import DashPlugin


class TracingPlugin(DashPlugin):
    def __init__(self, name: str = "tracing", app: Dash | None = None) -> None:
        super().__init__(name, app)
        self._tracer = trace.get_tracer(__name__)


class TracingTransform(DashTransform):
    def __init__(self):
        super().__init__()
        self.tracer = trace.get_tracer(__name__)

    def apply_serverside(self, callbacks):
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
        return callbacks
