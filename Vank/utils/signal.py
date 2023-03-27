import typing as t
from threading import Lock
from functools import wraps


class Signal:
    """
    信号是一种设计模式,解决了一对多的hard-code问题
    """

    def __init__(self):
        self.lock = Lock()
        self._binds: t.Dict[int, t.Callable] = {}

    def bind(self, listener: t.Callable, identify: int = None, *array, **kwargs):
        """
        绑定
        """

        with self.lock:
            if identify is None:
                identify = id(listener)
            self._binds[identify] = listener
            return identify

    def unbind(self, listener=None, identify=None):
        """
        取消绑定
        """
        if identify is None:
            identify = id(listener)
        with self.lock:
            del self._binds[identify]

    def emit(self, sender, *args, **kwargs):
        with self.lock:
            return [
                (identify, listener, listener(signal=self, sender=sender, *args, **kwargs))
                for identify, listener in self._binds.items()
            ]


configs_check = Signal()
on_start_up = Signal()
on_request_start = Signal()
on_request_end = Signal()
