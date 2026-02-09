import os.path as op
from os import makedirs
from typing import List
from collections import deque
from lepton.core.objects import Serializable


DEFAULT_HISTORY_LENGTH = 20

class AppData(Serializable):
    def __init__(self, history_length=DEFAULT_HISTORY_LENGTH, sidebar_visible=True):
        self.history = deque(maxlen=history_length)  # Queue to store last n opened files
        self.show_sidebar = sidebar_visible

    def add_to_history(self, file_path: str):
        if file_path in self.history:
            self.history.remove(file_path)
        self.history.append(file_path)
        self.save()

    def get_history(self) -> List[str]:
        return list(self.history)

    def save(self, app_data_f):
        makedirs(op.dirname(app_data_f), exist_ok=True)
        super().to_json(app_data_f)

    def to_dict(self, validate=False):
        data = super().to_dict(validate)
        data['history'] = list(self.history)
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.history = deque(data.get('history', []), maxlen=DEFAULT_HISTORY_LENGTH)
        return obj

def load_app_data(app_data_f) -> AppData:
    if not op.isfile(app_data_f):
        data = AppData()
        data.save(app_data_f)
        return data
    return AppData.from_json(app_data_f)
