from typing import List
from pydantic import BaseModel
from snapcheck.snap.elements import ElementUnion
from snapcheck.snap.rating import Rating


class BoardModel(BaseModel):
    title: str
    description: str
    # all_intended_ratings: List[RatingModel] # TODO add this or not ? (already in elements)
    style: dict[str, str]
    elements: List[ElementUnion]  # Use the union instead of AbstractElement


class SnapModel(BaseModel):
    title: str | None = None
    description: str | None = None
    metadata: dict
    ratings: List[Rating] = []
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
