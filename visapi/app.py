import typing as t
from collections import defaultdict
from pathlib import Path

from helpers.error import ErrorHandler
from visapi.routing import router
from visapi.interface.rsgi import handler as rsgi_handler
from visapi.interface.asgi import handler as asgi_handler


class VisAPI:
    rsgi_http_handler = rsgi_handler.HTTPHandler
    rsgi_websocket_handler = rsgi_handler.WebsocketHandler
    asgi_http_handler = asgi_handler.HTTPHandler
    asgi_websocket_handler = asgi_handler.WebsocketHandler
    asgi_lifespan_handler = asgi_handler.LifeSpanHandler
    router_cls = router.Router

    def __init__(self, project_root, config_path):
        self.handler_mapping = dict(
            rsgi_http_handler=self.rsgi_http_handler(self),
            rsgi_ws_handler=self.rsgi_websocket_handler(self),
            asgi_http_handler=self.asgi_http_handler(self),
            asgi_websocket_handler=self.asgi_websocket_handler(self),
            asgi_lifespan_handler=self.asgi_lifespan_handler(self),
        )
        if not (project_root := Path(project_root)).is_dir():
            raise ValueError('project_root is not a directory')
        self.project_root = project_root
        if not (config_path := Path(config_path)).is_file():
            raise ValueError('config_path is not a file')
        self.config_path = config_path
        self.router = self.router_cls()
        self.error_handler = ErrorHandler(self)

    def get(self, rule_path: str, name: t.Optional[str] = None):
        return self.router.get(rule_path, name)

    def post(self, rule_path: str, name: t.Optional[str] = None):
        return self.router.post(rule_path, name)

    def delete(self, rule_path: str, name: t.Optional[str] = None):
        return self.router.delete(rule_path, name)

    def put(self, rule_path: str, name: t.Optional[str] = None):
        return self.router.put(rule_path, name)

    def websocket(self, rule_path: str, name: t.Optional[str] = None):
        return self.router.websocket(rule_path, name)

    def mount_group(self, group: "router.GroupRouter"):
        return self.router.mount_group(group)

    def __call__(self, scope, receive, send):
        """
        ASGI entry-point function
        :param scope:
        :param receive:
        :param send:
        :return:
        """
        return self.handler_mapping[f"asgi_{scope['type']}_handler"](scope, receive, send)

    def __rsgi__(self, scope, proto):
        """
        RSGI entry-point function
        :param scope:
        :param proto:
        :return:
        """
        return self.handler_mapping[f"rsgi_{scope.proto}_handler"](scope, proto)
