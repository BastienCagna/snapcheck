from pathlib import Path
from typing import List
from lepton.core.objects import BSCObject
from time import time
import uuid

ID_LENGTH = 12



class ObjectStoreItem:
    path: str | Path
    object: BSCObject
    id: str
    last_access: float
    version: int

    def __init__(self, path: str | Path, object: BSCObject):
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


class LeptonSession:
    id: str
    last_access: float
    items: List[ObjectStoreItem] = []

    def __init__(self):
        self.id = uuid.uuid4().hex[:ID_LENGTH]
        self.last_access = time()

    def register_item(self, item: ObjectStoreItem):
        self.items.append(item)


class SessionStore:
    items: List[ObjectStoreItem] = []
    sessions: List[LeptonSession] = []
    loader: callable

    def get_all(self):
        return self.items

    def new_session(self) -> LeptonSession:
        session = LeptonSession()
        self.sessions.append(session)
        return session

    def close_session(self, sid: str, force=False) -> List[ObjectStoreItem] | None:
        session = self.get_session(sid)
        if not session:
            raise ValueError(f"Session with id {sid} not found")
        # Close all items where no other session is using them
        to_be_saved = []
        for item in session.items:
            if not any(item in s.items for s in self.sessions if s != session):
                if not self.close(item.id, force=force):
                    to_be_saved.append(item)
        if len(to_be_saved) > 0:
            return to_be_saved
        self.sessions.remove(session)
        return None

    def get_session(self, sid: str) -> LeptonSession:
        for session in self.sessions:
            if session.id == sid:
                session.last_access = time()
                return session
        raise ValueError(f"Session with id {sid} not found")

    def open(self, session_id: str, path: str) -> ObjectStoreItem:
        """Open a snap in the specified session.

        If the file has already been open, return it.
        """

        # Get the target session
        session = self.get_session(session_id)

        # Search if the snap (item) is already, open
        # If it is, register him in the session and return it
        for item in self.items:
            if item.object.path == path:
                if not item in session.items:
                    session.register_item(item)
                return item

        # Else, load the file
        new_item = ObjectStoreItem(path, self.loader(path))
        self.items.append(new_item)
        # And register it to this session
        session.register_item(new_item)
        return new_item

    def get_by_id(self, id: str) -> ObjectStoreItem | None:
        for item in self.items:
            if item.id == id:
                item.last_access = time()
                return item
        return None

    def close(self, id: str, force=False) -> bool:
        item = self.get_by_id(id)
        if not item:
            raise IOError(f"ObjectStoreItem with id {id} not found")

        if force or not item.object._has_changed:
            self.items.remove(item)
            return True

        return False
