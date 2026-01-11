from typing import List
from snapcheck.snap import Snap, load_snap
from time import time
import uuid
import os.path as op

SESSION_TIMEOUT = 12 * 3600
QCITEM_TIMEOUT = 12 * 3600

ID_LENGTH = 12


class SnapStoreItem:
    snap: Snap
    id: str
    last_access: float
    version: int

    def __init__(self, path):
        self._path = path
        self.snap = load_snap(path)
        self.id = uuid.uuid4().hex[:ID_LENGTH]
        self.last_access = time()
        self.version = 0

    def to_dict(self, clean=False) -> dict:
        ret_snap = self.snap.to_dict(compress=False, clean=clean)
        ret_snap["filename"] = op.split(self._path)[1] if self._path else None
        ret_snap["has_changed"] = self.snap._has_changed or False
        ret_snap["is_cancellable"] = len(self.snap._backups) > 0
        ret_snap["is_redoable"] = len(self.snap._forwups) > 0
        ret_snap["id"] = self.id
        ret_snap["version"] = self.version
        return ret_snap
    
    def increment_version(self):
        """Increment version after each modification"""
        self.version += 1


class SnapSession:
    id: str
    last_access: float
    items: List[SnapStoreItem] = []

    def __init__(self):
        self.id = uuid.uuid4().hex[:ID_LENGTH]
        self.last_access = time()

    def register_item(self, item: SnapStoreItem):
        self.items.append(item)


class SnapStore:
    items: List[SnapStoreItem] = []
    sessions: List[SnapSession] = []

    def get_all(self):
        return self.items

    def new_session(self) -> SnapSession:
        session = SnapSession()
        self.sessions.append(session)
        return session

    def close_session(self, sid: str, force=False) -> List[SnapStoreItem] | None:
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

    def get_session(self, sid: str) -> SnapSession:
        for session in self.sessions:
            if session.id == sid:
                session.last_access = time()
                return session
        raise ValueError(f"Session with id {sid} not found")

    def open(self, session_id: str, path: str) -> SnapStoreItem:
        """Open a snap in the specified session.

        If the file has already been open, return it.
        """

        # Get the target session
        session = self.get_session(session_id)

        # Search if the snap (item) is already, open
        # If it is, register him in the session and return it
        for item in self.items:
            if item.snap._path == path:
                if not item in session.items:
                    session.register_item(item)
                return item

        # Else, load the file
        new_item = SnapStoreItem(path)
        self.items.append(new_item)
        # And register it to this session
        session.register_item(new_item)
        return new_item

    def get_by_id(self, id: str) -> SnapStoreItem | None:
        for item in self.items:
            if item.id == id:
                item.last_access = time()
                return item
        return None

    def close(self, id: str, force=False) -> bool:
        item = self.get_by_id(id)
        if not item:
            raise IOError(f"SnapStoreItem with id {id} not found")

        if force or not item.snap._has_changed:
            self.items.remove(item)
            return True

        return False
