from contextlib import contextmanager
from uuid import uuid4
import json

from collections import deque
from copy import deepcopy
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
        self._is_loading = True
        yield
        self._is_loading = False

    def __post_init__(self, *args, **kwargs):
        pass

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

    def to_dict(self) -> dict:
        return serialize(self)

    def to_json(self, path: str, indent=4) -> None:
        """ Save the QualityControl
            This method allows to use an other default serialization method in future.
        """
        data = self.to_dict(validate=True)
        json.dump(data, open(path, 'w'), indent=indent)

    @classmethod
    def from_dict(cls, data: dict):
        all_attributes = globalDynamicLoader.get_all_attributes(cls).keys()

        # Inflate all objects
        obj = globalDynamicLoader.inflate(data)
        if "_is_loading" in all_attributes:
            obj._is_loading = True

        # Resolve references
        obj = resolve_references(obj)

        # saved_attributes = filter(lambda k: not k[0] == "_", all_attributes)
        # for attr in all_attributes:
        #     if attr not in saved_attributes:
        #         del obj[attr]          

        if hasattr(obj, "_is_loading"):
            obj._is_loading = False

        return obj


class Backupable:
    """
        A class that allows to create backups of its state and revert or restore changes.
    """
    _backups: deque
    _forwups: deque

    def __post_init__(self):
        self._backups = deque(maxlen=BACKUP_DEQUE_SIZE)
        self._forups = deque(maxlen=BACKUP_DEQUE_SIZE)
        if hasattr(self, 'has_changed') and not isinstance(self.has_changed, Callback):
            self.has_changed.connect(self.create_backup)

    def create_backup(self):
        self._backups.append(self.to_dict())

    def revert_changes(self):
        if len(self.backups):
            self._forwups.append(deepcopy(self.__dict__))
            previous_state = self._backups.pop()
            self._restore_from_deepcopy(previous_state)

    def restore_changes(self):
        if len(self.forwups):
            self._backups.append(deepcopy(self.__dict__))
            next_state = self._forwups.pop()
            self._restore_from_deepcopy(next_state)

    def _restore_from_deepcopy(self, state: dict):
        # Remplace les attributs actuels par ceux du dictionnaire passé
        # for key, value in state.items():
        #     setattr(self, key, value)
        self = self.from_dict(state)

    @contextmanager
    def changing(self):
        backup = self.to_dict()
        try:
            yield
        except Exception as e:
            self._restore_from_deepcopy(backup)
            raise e
        else:
            self._backups.append(backup)
            self.has_changed()


class BSCObject(Backupable, Serializable, Changeable):

    def __init__(self, *args, **attributes):
        Changeable.__init__(self, *args, **attributes)
        Serializable.__init__(self)
        Backupable.__init__(self)

    # def __post_init__(self, *args, **kwargs):
    #     Changeable.__post_init__(self, *args, **kwargs)
    #     Serializable.__post_init__(self, *args, **kwargs)
    #     Backupable.__post_init__(self, *args, **kwargs)