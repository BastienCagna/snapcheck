from contextlib import contextmanager
import sys
import importlib
import inspect
from typing import Callable
from PyQt5.QtCore import pyqtSignal
from .callback import Callback
from os import getcwd, chdir

try:  # Optional dependency: only needed to special-case Pydantic models during inflate
    from pydantic import BaseModel as _PydanticBaseModel  # type: ignore
except Exception:  # pragma: no cover - pydantic might not be installed
    _PydanticBaseModel = None


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

        # If we are dealing with a Pydantic model, use model_construct to create
        # the instance without validation (needed because references like "@._scales#0"
        # will be resolved later by resolve_references()).
        if _PydanticBaseModel is not None and isinstance(cls, type) and issubclass(cls, _PydanticBaseModel):
            model_data = {k: self.inflate(v) for k, v in data.items() if k != "__cls__"}
            # Use model_construct (v2) or construct (v1) to bypass validation
            # while properly initializing internal Pydantic attributes
            if hasattr(cls, "model_construct"):
                return cls.model_construct(**model_data)
            if hasattr(cls, "construct"):
                return cls.construct(**model_data)
            # Fallback: direct instantiation (may fail with validation)
            return cls(**model_data)

        # New instance of the object without calling __init__()
        obj = cls.__new__(cls)

        # Then set all the attribute from dict data
        cls_attributes = self.get_all_attributes(cls).keys()
        all_attributes = set(list(cls_attributes) + list(data.keys()))
        
        if "_is_loading" in all_attributes:
            obj._is_loading = True

        for attr in all_attributes:
            if attr == "_is_loading" or attr == "has_changed":
                continue
            val = data[attr] if attr in data else None
            obj.__setattr__(attr, self.inflate(val))

        if hasattr(obj, "_is_loading"):
            obj._is_loading = False

        return obj
    

def resolve_references(data, ref_data=None):
    """Replace any string starting by "@." by the target value. 
    
        Objects must already inflated to avoid unwanted duplicates
    """
    if ref_data is None:
        ref_data = data

    if isinstance(data, list):
        return list(resolve_references(item, ref_data) for item in data)
    elif isinstance(data, tuple):
        return tuple(resolve_references(item, ref_data) for item in data)
    elif isinstance(data, dict):
        return {k: resolve_references(item, ref_data) for k, item in data.items()}
    elif hasattr(data, "__dict__"):
        for attr, value in data.__dict__.items():
            setattr(data, attr, resolve_references(value, ref_data))
        return data
    # Resolve references
    elif isinstance(data, str) and data.startswith("@."):
        # It's a reference: "@.<attribute.subattribute>(#<index>)"
        # Parse the reference address
        if "#" in data:
            splt = data.split('#')
            addr = splt[0]
            index = int(splt[1])
        else:
            addr = data
            index = None
        attrs = addr[2:].split(".")
        # Find the target data and inflate
        # FIXME: what append when the target is already inflated ?
        data = ref_data
        for attr in attrs:
            data = getattr(ref_data, attr)
        if index is not None:
            data = data[index]
        return resolve_references(data, ref_data)
    return data



globalDynamicLoader = DynamicLoader()
