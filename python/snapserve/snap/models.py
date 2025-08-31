from typing import List
from pydantic import BaseModel


class RatingScaleItem(BaseModel):
    name: str
    value: int
    description: str
    color: str | None = None

class RatingScaleModel(BaseModel):
    description: str
    ratings: List[RatingScaleItem]

class RatingModel(BaseModel):
    id: str
    name: str
    description: str
    scale:RatingScaleModel | None
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
    intended_ratings: List[RatingModel]
    style: dict[str, str]
    elements:List[ImageElementModel]

class SnapModel(BaseModel):
    title: str | None = None
    description: str | None = None
    metadata: dict
    ratings: List[RatingModel] = []
    boards: List[BoardModel] = []

    id: str | None = None
    has_changed: bool = False
    filename: str | None = None
    is_cancellable: bool = False
    is_redoable: bool = False

class SnapShortModel(BaseModel):
    title: str | None = None
    description: str | None = None
    id: str | None = None
    has_changed: bool = False
    filename: str | None = None

class SnapCheckSessionModel(BaseModel):
    id: str
    last_access: float
    items: List[SnapShortModel] = []
