import os.path as op
import json
from os import makedirs

from snapcheck.core.objects import Serializable
from typing import List
from collections import deque
from snapserve.app_settings import APP_SETTINGS

APP_DATA_PATH = op.join(APP_SETTINGS.get("core.share_dir").value, "app_data.json")

class AppData(Serializable):
    def __init__(self):
        self.history = deque(maxlen=APP_SETTINGS.get("files.n_history").value)  # Queue to store last n opened files
        self.show_sidebar = True

    def add_to_history(self, file_path: str):
        if file_path in self.history:
            self.history.remove(file_path)
        self.history.append(file_path)
        self.save()

    def get_history(self) -> List[str]:
        return list(self.history)

    def save(self):
        makedirs(op.dirname(APP_DATA_PATH), exist_ok=True)
        super().to_json(APP_DATA_PATH)

    def to_dict(self, validate=False):
        data = super().to_dict(validate)
        data['history'] = list(self.history)
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.history = deque(data.get('history', []), maxlen=APP_SETTINGS.get("files.n_history").value)
        return obj

def load_app_data() -> AppData:
    if not op.isfile(APP_DATA_PATH):
        data = AppData()
        data.save()
        return data
    return AppData.from_json(APP_DATA_PATH)

APP_DATA = load_app_data()