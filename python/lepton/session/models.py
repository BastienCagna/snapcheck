from pathlib import Path
from typing import List
from time import time
import uuid
from pydantic import BaseModel
from lepton_common import LObject


ID_LENGTH = 12

    
class ObjectModel(BaseModel):
    title: str | None = None
    description: str | None = None
    metadata: dict

    id: str | None = None
    has_changed: bool = False
    filename: str | None = None
    is_cancellable: bool = False
    is_redoable: bool = False


class ObjectShortModel(BaseModel):
    title: str | None = None
    description: str | None = None
    id: str | None = None
    has_changed: bool = False
    filename: str | None = None


class SessionModel(BaseModel):
    id: str
    last_access: float
    items: List[ObjectShortModel] = []


class SessionWithTokenModel(SessionModel):
    token: str | None = None


class ObjectStoreItem:
    path: str | Path
    object: LObject
    id: str
    last_access: float
    version: int

    def __init__(self, path: str | Path, object: LObject):
        self.path = path
        self.object = object
        self.id = uuid.uuid4().hex[:ID_LENGTH]
        self.last_access = time()
        self.version = 0

    def to_dict(self, clean=False) -> dict:
        ret_snap = self.object.to_dict(compress=False, clean=clean)
        ret_snap["filename"] = Path(self.path).name if self.path else None
        ret_snap["has_changed"] = self.object._has_changed or False
        ret_snap["is_cancellable"] = len(self.object._backups) > 0
        ret_snap["is_redoable"] = len(self.object._forwups) > 0
        ret_snap["id"] = self.id
        ret_snap["version"] = self.version
        return ret_snap

    def increment_version(self):
        """Increment version after each modification"""
        self.version += 1


class LSession:
    id: str
    last_access: float
    items: List[ObjectStoreItem] = []

    def __init__(self, id: str | None = None):
        self.id = id if id is not None else uuid.uuid4().hex[:ID_LENGTH]
        self.last_access = time()

    def register_item(self, item: ObjectStoreItem):
        self.items.append(item)
