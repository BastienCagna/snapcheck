from typing import List
from time import time

from lepton.session.models import LSession, ObjectStoreItem
from lepton_common.objects import IOHelper


class SessionStore:
    """
    The SessionStore handles the user sessions and the loaded files. It is the main interface to manage
    the usefull payload of the app.

    Items
    -----
    An item is created when a file is opened for the first time, and is removed when it is closed and no session is using it. 
    Each item has a unique id, a path, and a reference to the loaded object.

    Sessions
    --------
    A session is created when a user connects to the app, and is closed when the user disconnects.
    Each session has a unique id, and can have multiple items (files) open. 
    When a session is closed if no other session is using items, they are removed from the store.

    """
    items: List[ObjectStoreItem] = []
    sessions: List[LSession] = []
    io: IOHelper

    def __init__(self, io: IOHelper):
        self.io = io

    def get_all(self):
        return self.items

    def new_session(self) -> LSession:
        """ Create and register a new empty session """
        session = LSession()
        self.sessions.append(session)
        return session

    def close_session(self, sid: str, force=False) -> List[ObjectStoreItem] | None:
        """ Close the session matching the given id.

        """
        # Get the session
        session = self.get_session(sid)
        if not session:
            raise ValueError(f"Session with id {sid} not found")
        
        # Close all items where no other session is using them
        to_be_saved = []
        for item in session.items:
            if not any(item in s.items for s in self.sessions if s != session):
                if not self.close(item.id, force=force):
                    # If the item can not be closed, register it to be saved later.
                    to_be_saved.append(item)
        if len(to_be_saved) > 0:
            return to_be_saved
        
        # If no item is blocking the session closing, close it and remove it from the store
        self.sessions.remove(session)
        return None

    def get_session(self, sid: str) -> LSession:
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
        new_item = ObjectStoreItem(path, self.io.open(path))
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
    
    def save(self, id: str) -> bool:
        raise NotImplementedError("Saving is not implemented yet")

    def close(self, id: str, force=False) -> bool:
        """ Close an item. 
        
        If force is False, the item will be closed only if it has not changed. 
        """
        # Get the item
        item = self.get_by_id(id)
        if not item:
            raise IOError(f"ObjectStoreItem with id {id} not found")

        # If the item has not changed or if force is True, close it
        if force or not item.object._has_changed:
            self.items.remove(item)
            return True

        # Else, if it has changed and force is False, do not close it and return False
        return False
