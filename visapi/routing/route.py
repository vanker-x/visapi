import asyncio
import inspect
import re
import typing as t
from functools import partial, update_wrapper
from visapi.exceptions import MethodNotAllowed, NotFound
from visapi.routing.convertor import Convertor, IntConvertor, StrConvertor, FloatConvertor

build_rule_regex = re.compile(
    r"(?P<static>[^{]*){(?P<var>[a-zA-Z_][a-zA-Z_0-9]*):(?P<convertor>[a-zA-Z_][a-zA-Z_0-9]*)}"
)


class SyncToAsyncWrapper:
    def __init__(self, callback: t.Callable, dynamic: t.Dict[str, t.Any] = None):
        self.dynamic = dynamic or {}
        self.callback = callback
        update_wrapper(self, callback)

    async def __call__(self, *args, **kwargs):
        data = self.dynamic | kwargs
        if not inspect.iscoroutinefunction(self.callback):
            return await asyncio.to_thread(self.callback, *args, **data)
        return await self.callback(*args, **data)


def get_rule_part(rule_path: str):
    start = 0
    end = len(rule_path)
    while start < end:
        res = build_rule_regex.search(rule_path, pos=start)
        if not res:
            break
        group_dict = res.groupdict()
        yield group_dict["static"], group_dict["var"], group_dict["convertor"]
        start = res.end()
    if start < end:
        legacy_route = rule_path[start:]
        if '{' in legacy_route or '}' in legacy_route:
            raise SyntaxError(f'Incorrect rule syntax. Should not appear single "{" or "}" in {legacy_route}')
        yield legacy_route, None, None


convertors = {
    "int": IntConvertor(),
    "str": StrConvertor(),
    "float": FloatConvertor(),
}


class Route:
    protocol: str = None
    partial_route: bool = False  # Controls whether compiled regular expressions end with $

    def __init__(self, rule_path: str, callback: callable, name: str):
        self.rule_path: str = rule_path
        self.callback: t.Callable = callback
        self.name: str = name
        self.dynamic: t.Dict = {}
        self.regex: t.Optional[re.Pattern] = None
        self.build()

    def build(self):
        regex_part = []
        for static, variable, convertor_name in get_rule_part(self.rule_path):
            # we need escape plain string
            regex_part.append(re.escape(static))
            if convertor_name is None:
                continue
            if variable in self.dynamic:
                raise SyntaxError(f"Duplicate keyword parameters '{variable}' cannot appear in same route path")
            convertor = convertors.get(convertor_name, None)
            if convertor is None:
                raise SyntaxError(f"Convertor '{convertor_name}' does not exist.")
            self.dynamic[variable] = convertor
            regex_part.append(f"(?P<{variable}>{convertor.regex})")
        regex_str = f"^{''.join(regex_part)}"
        if not self.partial_route:
            regex_str += "$"
        self.regex = re.compile(regex_str)

    def get_callback(self, path, **extra) -> t.Tuple[t.Optional[t.Callable], t.Optional[t.Dict[str, t.Any]]]:
        raise NotImplementedError("Subclass must implement get_callback method")

    def to_dict(self) -> t.Dict[str, t.Any]:
        raise NotImplementedError("Subclass must implement to_dict method")

    def convert(self, dynamic: dict) -> t.Dict[str, t.Any]:
        for key, convertor in self.dynamic.items():
            dynamic[key] = convertor.to_python(dynamic[key])
        return dynamic


class GroupRoute(Route):
    partial_route = True  # means that we just match the beginning part

    def get_callback(self, path, **extra) -> t.Optional[SyncToAsyncWrapper]:
        if not (res := self.regex.match(path)):
            return None
        # Call the GroupRouter to get the real handler
        extra["path_match_end"] = res.end()
        extra["dynamic"] = res.groupdict()
        try:
            callback = self.callback(path, **extra)
        except NotFound as e:
            # To catch the NotFound thrown by the GroupRouter and drown it
            return None
        return callback


class HTTPRoute(Route):
    protocol = "http"

    def __init__(self, rule_path: str, methods: t.List[str], callback: t.Callable, name: str):
        methods = [str(method).upper() for method in methods]
        assert methods, "Methods must be HTTP protocol method list"
        self.methods = methods
        super().__init__(rule_path, callback, name)

    def get_callback(self, path, **extra) -> t.Optional[SyncToAsyncWrapper]:
        protocol = extra.pop("protocol", None)
        if protocol is not None and not protocol == self.protocol:
            return None
        path_match_end = extra.pop("path_match_end", 0)
        method = extra.pop("method", "GET")
        path = path[path_match_end:]
        if not (res := self.regex.match(path)):
            return None

        if (method := method.upper()) not in self.methods:
            raise MethodNotAllowed(method, self.methods)
        dynamic = extra.pop("dynamic", {})
        dynamic |= res.groupdict()
        return SyncToAsyncWrapper(self.callback, self.convert(dynamic))


class WebSocketRoute(Route):
    protocol = "websocket"

    def get_callback(self, path, **extra) -> t.Optional[SyncToAsyncWrapper]:
        protocol = extra.pop("protocol", None)
        if protocol is not None and not protocol == self.protocol:
            return None
        path_match_end = extra.pop("path_match_end", 0)
        path = path[path_match_end:]
        if not (res := self.regex.match(path)):
            return None
        dynamic = extra.pop("dynamic", {})
        dynamic |= res.groupdict()
        return SyncToAsyncWrapper(self.callback, self.convert(dynamic))
