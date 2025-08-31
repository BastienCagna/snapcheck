from dataclasses import dataclass, field
from typing import List

@dataclass
class RatingScaleItem:
    name: str = ""
    value: int = 0
    description: str = ""
    color: str|None = None


@dataclass
class RatingScale:
    description: str = ""
    ratings: List[RatingScaleItem] = field(default_factory=list)

    def check(self):
        """Verify the object content integrity.

            Note names and values must be unique.
        """
        names = []
        values = []
        for rating in self.ratings:
            if rating.name in names:
                raise ValueError(f"Duplicate rating name: {rating.name}")
            names.append(rating.name)
            if rating.value in values:
                raise ValueError(f"Duplicate rating value: {rating.value}")
            values.append(rating.value)



@dataclass
class Rating:
    """
        A rating with a scale for quality control.
        Attributes:
            id: Unique identifier for the rating.
            name: Name of the rating.
            description: Description of the rating.
            scale: Scale used for the rating, which can be a NoteScale object.
            value: Value of the rating based on the scale.
            comment: Optional comment for additional information.

        Scale can be leaved None if only comment will be used.
    """
    id: str|None = None
    name: str = ""
    description: str = ""
    scale: RatingScale|None = None

    value: int|None = None
    comment: str|None = None

    def __post_init__(self):
        if self.id is None:
            # If not provided, generate an ID from the name
            self.id = self.name.lower().replace(" ", "_")
