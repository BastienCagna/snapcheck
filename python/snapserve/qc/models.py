from typing import List
from pydantic import BaseModel


class NoteScaleItem(BaseModel):
    name: str
    value: int
    description: str
    color: str | None = None

class NoteScaleModel(BaseModel):
    description: str
    notes: List[NoteScaleItem]

class NoteModel(BaseModel):
    id: str
    name: str
    description: str
    scale:NoteScaleModel | None
    value: int|None
    comment: str|None

class ElementModel(BaseModel):
    type: str
    style: dict[str, str] = {}  # Element CSS style
    title: str | None = None  # Optional title for the element, e.g., "Input DWI (b=0)"

class ImageElementModel(ElementModel):
    type: str = "image"
    src: str = ""  # Source of the image file, e.g., "input_dwi.png"

class BoardModel(BaseModel):
    title: str
    description: str
    intended_notes: List[NoteModel]
    style: dict[str, str]
    elements:List[ImageElementModel]

class QualityControlModel(BaseModel):
    title: str | None = None
    description: str | None = None
    metadata: dict
    notes: List[NoteModel] = []
    boards: List[BoardModel] = []

    has_changed: bool = False
    filename: str | None = None
    is_cancellable: bool = False
    is_redoable: bool = False