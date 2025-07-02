from contextlib import contextmanager
import sys
import importlib
import inspect
from typing import Callable
from warnings import warn
from PyQt5.QtCore import pyqtSignal
from .callback import Callback
import os.path as op
from os import getcwd, chdir

@contextmanager
def temporarly_change_directory(target_dir: str):
    memo = getcwd()
    chdir(target_dir)
    yield
    chdir(memo)

def serialize(obj):
    """Return the string version of objetcs or variables

    For objects, it serialize all attribute not starting by "_" and
    store the python path to the class definition in the attribute
    named "__cls__".
    """
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {serialize(key): serialize(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [serialize(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        attributes = {}
        for key, value in obj.__dict__.items():
            if not key.startswith("_") and not isinstance(value, (pyqtSignal, Callback)):
                attributes[key] = serialize(value)
        attributes["__cls__"] = obj.__module__ + "." + obj.__class__.__name__
        return attributes
    else:
        return str(obj)


class DynamicLoader:
    """A class to centralized the dynamic module import needed to reload serialized objects

    N.B: Use globalDynamicLoader (see below) to avoid multiple module loadings

    """

    def __init__(self):
        self.modules = {}

    def get_module(self, module_name: str):
        """Return the module and import it if needed."""
        if module_name in sys.modules:
            return sys.modules[module_name]

        if module_name in self.modules:
            return self.modules[module_name]

        # Import the module
        module = importlib.import_module(module_name)
        # Manually add the module to the imported
        self.modules[module_name] = module

    def get_function(self, function_path: str) -> Callable:
        """Return the function
        The function path is a python path: package.module.submodule.the_function
        """
        splt_path = function_path.split(".")
        obj_module_path = ".".join(splt_path[:-1])
        func_name = splt_path[-1]
        module = self.get_module(obj_module_path)
        func = getattr(module, func_name, None)
        if func is None or not callable(func):
            return None
        return func

    def clean(self):
        self.modules = {}

    def get_all_attributes(self, cls):
        """List all attributes defined by the class and its parents."""
        attributes = inspect.get_annotations(cls)

        for base in cls.__bases__:
            attributes.update(self.get_all_attributes(base))

        return attributes

    def inflate(self, data: dict):
        if isinstance(data, list):
            return list(self.inflate(item) for item in data)
        if isinstance(data, tuple):
            return tuple(self.inflate(item) for item in data)
        if not isinstance(data, dict) or not "__cls__" in data:
            return data

        splt_path = data["__cls__"].split(".")
        obj_module_path = ".".join(splt_path[:-1])
        obj_class = splt_path[-1]

        # Get the module
        module = self.get_module(obj_module_path)

        # Ge the class
        cls = getattr(module, obj_class)

        # New instance of the object without calling __init__()
        obj = cls.__new__(cls)

        # The set all the attribute from dict data
        all_attributes = self.get_all_attributes(cls).keys()
        saved_attributes = filter(lambda k: not k[0] == "_", all_attributes)
        for attr in saved_attributes:
            if attr in data:
                val = data[attr]
            else:
                val = None
                warn(f'No value for "{cls.__name__}.{attr}" in serialized data. Setting it to None.')
            obj.__setattr__(attr, self.inflate(val))

        if hasattr(obj, "_loading"):
            obj.__setattr__("_loading", False)

        return obj

globalDynamicLoader = DynamicLoader()
