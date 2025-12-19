from typing import List
from pydantic import BaseModel


class DirectoryItemModel(BaseModel):
    path: str
    filename: str
    isdir: bool

class DirectoryModel(BaseModel):
    path: str
    content: List[DirectoryItemModel]
    parent: str | None = None

# class FileModel(BaseModel):
#     description: str
#     notes: List[NoteScaleItem]
