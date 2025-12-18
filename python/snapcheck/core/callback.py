import inspect
from typing import Callable


class Callback:
    """
    The callback allows to call multiple functions with variable arguments when .emit() is called.
    """

    callbacks: list

    def __init__(self):
        self.callbacks = []

    def connect(self, func: Callable):
        """Register a function to be called when .emit() is called."""
        self.callbacks.append((func, inspect.signature(func).parameters.values()))

    def disconnect(self, func: Callable):
        """Unregister a function."""
        self.callbacks = [cb for cb in self.callbacks if cb[0] != func]

    def emit(self, *args):
        """Call all registered functions with the provided arguments."""
        for func, inputs in self.callbacks:
            if len(args) > len(inputs):
                f_args = args[: len(inputs)]
            else:
                f_args = args
            func(*f_args)

    def __call__(self, *args):
        self.emit(*args)
