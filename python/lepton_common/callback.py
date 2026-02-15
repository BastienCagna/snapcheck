import inspect
from typing import Callable


class Callback:
    """ Callback can be used to create simple signal/slot mechanism.

    Several functions can be connected to the callback, and when the callback is emitted,
    all connected functions are called with the provided arguments.

    The registered functions can have different signatures. When the callback is emitted,
    only the arguments that match the function signature are passed to it.
    
    Example:

        def on_change(value):
            print("Value changed:", value)

        cb = Callback()
        cb.connect(on_change)
        cb.emit(42)  # This will call on_change(42)
    """
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