from typing import List
from pydantic import BaseModel


class NoteScaleModel(BaseModel):
    description: str
    notes: dict[int, str]

class NoteModel(BaseModel):
    id: str
    name: str
    description: str
    scale:NoteScaleModel | None
    value: int|None
    comment: str|None

class ElementModel(BaseModel):
    component: str
    props: dict[str, str]
    style: dict[str, str]

class BoardModel(BaseModel):
    title: str
    description: str
    intended_notes: List[str]  # List of note IDs that this board intends to use
    style: dict[str, str]
    elements:List[ElementModel]

class QualityControlModel(BaseModel):
    data_coordinates: dict
    notes: List[NoteModel] = []
    boards: List[BoardModel] = []