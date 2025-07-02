import inspect
from typing import Callable


class Callback:
    callbacks: list

    def __init__(self):
        self.callbacks = []

    def connect(self, func: Callable):
        self.callbacks.append((func, inspect.signature(func).parameters.values()))

    def disconnect(self, func: Callable):
        self.callbacks = [cb for cb in self.callbacks if cb[0] != func]

    def emit(self, *args):
        for func, inputs in self.callbacks:
            if len(args) > len(inputs):
                f_args = args[: len(inputs)]
            else:
                f_args = args
            func(*f_args)

    def __call__(self, *args):
        self.emit(*args)