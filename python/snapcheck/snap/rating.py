from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class RatingScaleItem(BaseModel):
    name: str = ""
    value: int = 0
    description: str = ""
    color: Optional[str] = None


class RatingScale(BaseModel):
    description: str = ""
    ratings: List[RatingScaleItem] = Field(default_factory=list)

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


class Rating(BaseModel):
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
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    scale: Optional[RatingScale] = None

    value: Optional[int] = None
    comment: Optional[str] = None

    @model_validator(mode='after')
    def generate_id(self):
        if self.id is None and self.name:
            # If not provided, generate an ID from the name
            self.id = self.name.lower().replace(" ", "_")
        return self

