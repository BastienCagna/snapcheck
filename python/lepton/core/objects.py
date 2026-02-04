from contextlib import contextmanager
from dataclasses import dataclass
from uuid import uuid4
import json

from collections import deque

from .io import globalDynamicLoader, resolve_references, serialize
from .callback import Callback

BACKUP_DEQUE_SIZE = 40


class Changeable:
    """
    A class that automatically emits a signal when an attribute is changed.

    Use the self.no_changed_signal() context manager to prevent the signal from being emitted
    during initialization or bulk updates.
    """

    has_changed: Callback
    _is_loading: bool = True
    _has_changed: bool = False

    def __init__(self, *args, **attributes):
        with self.no_changed_signal():
            self.has_changed = Callback()
            self.__post_init__(*args, **attributes)

    @contextmanager
    def no_changed_signal(self):
        """ A context manager to prevent the has_changed signal from being emitted. """
        self._is_loading = True
        yield
        self._is_loading = False

    def __post_init__(self, *args, **kwargs):
        self._has_changed = False

    def __setattr__(self, name, value):
        ret = super().__setattr__(name, value)
        if name[0] != "_" and not self._is_loading:
            self._has_changed = True
            self.has_changed.emit(self)
        return ret


class Serializable:
    """
    A class that recursively serializes its attributes to a dictionary.
    The serialized dictionary can be used to recreate the object later.
    An id attribute is automatically generated for each instance.
    """

    id = uuid4()

    def to_dict(self, validate=False, clean=False) -> dict:
        """
        Serialize to dictionary

        Args:
            validate: If True, validate the serialized data
            clean: If True, remove internal metadata like __cls__
        """
        data = serialize(self)

        if clean:
            return self._clean(data)

        return data

    def _clean(self, obj):
        """Recursively remove internal metadata"""
        if isinstance(obj, dict):
            cleaned = {}
            for k, v in obj.items():
                if k == "__cls__":
                    continue
                if k.startswith("_"):
                    continue
                cleaned[k] = self._clean(v)
            return cleaned
        elif isinstance(obj, list):
            return [self._clean(item) for item in obj]
        return obj

    def to_json(self, path: str, indent=4) -> None:
        """Serialize as JSON content
        This method allows to use an other default serialization method in future.
        """
        data = self.to_dict(validate=True)
        json.dump(data, open(path, "w"), indent=indent)

    @classmethod
    def from_dict(cls, data: dict, decompress=True):
        all_attributes = globalDynamicLoader.get_all_attributes(cls).keys()

        # Inflate all objects
        obj = globalDynamicLoader.inflate(data)
        if hasattr(obj, "__post_init__") and callable(obj.__post_init__):
            obj.__post_init__()

        if not decompress:
            return obj

        if "_is_loading" in all_attributes:
            obj._is_loading = True

        # Resolve references
        obj = resolve_references(obj)

        if hasattr(obj, "_is_loading"):
            obj._is_loading = False

        return obj

    @classmethod
    def from_json(cls, path: str) -> "Serializable":
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class Backupable(Serializable):
    """
    A class that allows to create backups of its state and revert or restore changes.
    """

    def __post_init__(self):
        # Initialize deques per instance to avoid sharing between objects
        self._backups = deque(maxlen=BACKUP_DEQUE_SIZE)
        self._forwups = deque(maxlen=BACKUP_DEQUE_SIZE)
        
        if hasattr(self, "has_changed") and isinstance(self.has_changed, Callback):
            self.has_changed.connect(self.create_backup)

    def revert_changes(self):
        """ Go back to the previous state """
        if len(self._backups):
            self._forwups.append(self.to_dict())
            previous_state = self._backups.pop()
            self._restore_from_deepcopy(previous_state)

    def restore_changes(self):
        """ Redo the last reverted change """
        if len(self._forwups):
            self._backups.append(self.to_dict())
            next_state = self._forwups.pop()
            self._restore_from_deepcopy(next_state)

    def _restore_from_deepcopy(self, state: dict):
        """Restore object state from a serialized dictionary.
        Preserves backup history (_backups, _forwups) by not overwriting these specific attributes.
        """
        restored = self.from_dict(state)
        # Save backup history before restoration
        saved_backups = self._backups
        saved_forwups = self._forwups
        # Restore all attributes (including private ones like _has_changed, etc.)
        self.__dict__.update(restored.__dict__)
        # Restore backup history
        self._backups = saved_backups
        self._forwups = saved_forwups

    @contextmanager
    def changing(self):
        """ A context manager to group multiple changes into a single backup. 
        
        Example:
            with obj.changing():
                obj.attr1 = new_value1
                obj.attr2 = new_value2
        """
        backup = self.to_dict()
        try:
            yield
        except Exception as e:
            self._restore_from_deepcopy(backup)
            raise e
        else:
            self._backups.append(backup)
            if hasattr(self, "has_changed") and isinstance(self.has_changed, Callback):
                self.has_changed()


class BSCObject(Backupable, Changeable):

    def __init__(self, *args, **attributes):
        Changeable.__init__(self, *args, **attributes)
        Backupable.__init__(self)

    def __post_init__(self, *args, **kwargs):
        Changeable.__post_init__(self, *args, **kwargs)
        Backupable.__post_init__(self, *args, **kwargs)
