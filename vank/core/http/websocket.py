import json
import typing as t
from enum import IntEnum
from urllib.parse import parse_qsl
from functools import cached_property
from vank.core.http.request import ASGIHeader
from vank.utils.datastructures import QueryString


class WebSocketState(IntEnum):
    """
    The state of the websocket connection lifecycle, each state
    will be presented in the tuple of (state value, phrase, [allowed ASGI types])
    """

    def __new__(cls, value: int, phrase, allowed_type=None):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        obj.allowed_type = allowed_type or tuple()
        return obj

    ClientConnecting = 0, "client_connecting", ("websocket.close",)
    Connecting = 1, "connecting", ("websocket.close",)
    Connected = 2, "connected", ("websocket.close",)
    Accepting = 3, "accepting", ("websocket.close", "websocket.accept")
    Accepted = 4, "accepted", ("websocket.close", "websocket.send")
    Closing = 5, "closing", ("websocket.close",)
    Closed = 6, "closed"


class WebsocketException(Exception):
    pass


class WebsocketClosed(WebsocketException):
    pass


class StateException(WebsocketException):
    def __init__(self, message: str, *expect: WebSocketState, got: WebSocketState):
        """
        When the current state is not the expected state exception
        :param message: error message
        :param expect: expected states
        :param got: current state
        """
        self.message = message
        self.expect = expect
        self.got = got


def _state_expection_wrapper(*states, mode: t.Optional[t.Literal["include", "exclude"]] = "include"):
    def decorator(fn):
        def inner(self: "WebSocket", *args, **kwargs):
            expection = self.state in states if mode == "include" else self.state not in states
            if not expection:
                raise StateException(
                    f'Expected {mode} "{",".join(ex.phrase for ex in states)}" states '
                    f'but got "{self.state.phrase}" currently',
                    *states,
                    got=self.state
                )
            return fn(self, *args, **kwargs)

        return inner

    return decorator


class WebSocket(ASGIHeader):
    def __init__(self, scope, receive, send):
        super().__init__(scope, receive)
        self._send = send
        self.state = WebSocketState.ClientConnecting

    @property
    def query(self) -> QueryString:
        """
        The query parameters for the current webSocket Connection
        :return: QueryString object
        """
        if not hasattr(self, "_query"):
            query = QueryString()
            qs = self._scope.get("query_string", b"").decode('latin-1')
            for key, value in parse_qsl(qs, keep_blank_values=True):
                query.append_value(key, value, error=False)
            self._query = query
        return self._query

    @cached_property
    def path(self) -> str:
        """
        Path for current websocket connection
        :return:
        """
        return self._scope.get("path")

    @property
    def is_closed(self) -> bool:
        """
        Return the current state is WebSocketState.
        :return: boolean value
        """
        return self.state == WebSocketState.Closed

    @_state_expection_wrapper(WebSocketState.ClientConnecting)
    async def connect(self):
        """
        Handle connect the websocket
        :return: connecting message
        """
        self.state = WebSocketState.Connecting
        message = await self.recv()
        return message

    @_state_expection_wrapper(WebSocketState.Connected)
    async def accept(self, subprotocol=None, headers=None):
        """
        Handle accpet the client websocket connection, and this operation must be done after the connect method
        :param subprotocol: subprotocol the server wishes to accept
        :param headers: an iterable of [name, value] two-item iterables.
        :return: nothing
        """
        self.state = WebSocketState.Accepting
        message = dict(
            type="websocket.accept",
            subprotocol=subprotocol,
            headers=headers or []
        )
        message = await self.send(message)
        self.state = WebSocketState.Accepted
        return message

    async def recv(self):
        """
        Handle receives a websocket message. If the state of websocket is closed, it will raise WebsocketClosed exception
        and if it receives a message with a type parameter of "websocket.disconnect",
        it will change the state of the websocket object to closed
        :return: received message
        """
        if self.state in (WebSocketState.Closed, WebSocketState.Closing):
            raise WebsocketClosed(f"websocket is {self.state.phrase} , can not receive message anymore")
        message = await self._receive()
        # handle websocket client disconnect
        if message.get("type") == "websocket.disconnect":
            self.state = WebSocketState.Closed
            raise WebsocketClosed("connection is disconnect from client")
        elif message.get("type") == "websocket.connect":  # handle proces connect event
            self.state = WebSocketState.Connected
        return message

    @_state_expection_wrapper(WebSocketState.Accepted)
    async def recv_text(self) -> str:
        data = await self.recv()
        return data.get("text", "")

    @_state_expection_wrapper(WebSocketState.Accepted)
    async def recv_bytes(self) -> bytes:
        data = await self.recv()
        return data.get("bytes", b"")

    @_state_expection_wrapper(WebSocketState.Accepted)
    async def recv_json(self, location: t.Optional[t.Literal["text", "bytes"]] = "text"):
        data = await self.recv()
        return json.loads(data.get(location, ""))

    @_state_expection_wrapper(WebSocketState.Closed, WebSocketState.Closing, mode="exclude")
    async def close(self, code: t.Optional[int] = 1000, reason: t.Optional[str] = None):
        """
        Proactively closing the connection with the client
        :param code: default is 1000
        :param reason: close reason
        :return: nothing
        """
        self.state = WebSocketState.Closing
        message = dict(
            type="websocket.close",
            code=code,
            reason=reason
        )
        await self.send(message)
        self.state = WebSocketState.Closed

    async def send(self, message: dict):
        """
        Send a messages to the client, and it may cause the following exceptions:
        WebsocketException: Sending the incorrect type parameter message in the current state
        :param message: message you want to send
        :return: nothing
        """
        if self.state == WebSocketState.Closed:
            raise WebsocketClosed("websocket is already been closed can not send message anymore")
        _type = message["type"]
        if _type not in self.state.allowed_type:
            raise WebsocketException(f"Incorrect type parameter of message, "
                                     f"current state of websocket is {self.state.phrase} "
                                     f"and the type parameter only support "
                                     f"{','.join(self.state.allowed_type)} not {_type}")
        data = await self._send(message)
        return data
