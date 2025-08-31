import os.path as op
import json

from snapcheck.core.objects import Serializable
from typing import List
from collections import deque
from snapserve.app_settings import APP_SETTINGS

APP_DATA_PATH = op.join(APP_SETTINGS.get("core.share_dir"), "app_data.json")

class AppData(Serializable):
    def __init__(self):
        self.history = deque(maxlen=APP_SETTINGS.get("files.n_history").value)  # Queue to store last n opened files

    def add_to_history(self, file_path: str):
        if file_path in self.history:
            self.history.remove(file_path)
        self.history.append(file_path)

    def get_history(self) -> List[str]:
        return list(self.history)


def load_app_data() -> AppData:
    if not op.isfile(APP_DATA_PATH):
        return AppData()
    return AppData.from_json(APP_DATA_PATH)

APP_DATA = load_app_data()