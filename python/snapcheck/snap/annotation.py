import uuid

from pydantic import BaseModel


class Annotation(BaseModel):
    id: str = ""

    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0

    # CSS style color
    color: str = "red"

    text: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class CircleAnnotation(Annotation):
    radius: float = 10.0


class RectangleAnnotation(Annotation):
    width: float = 10.0
    height: float = 10.0


class ArrowAnnotation(Annotation):
    length: float = 10.0
    width: float = 2.0
