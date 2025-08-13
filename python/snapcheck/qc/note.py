from dataclasses import dataclass, field
from typing import List

@dataclass
class NoteScaleItem:
    name: str = ""
    value: int = 0
    description: str = ""
    color: str|None = None


@dataclass
class NoteScale:
    description: str = ""
    notes: List[NoteScaleItem] = field(default_factory=list)

    def check(self):
        """Verify the object content integrity.

            Note names and values must be unique.
        """
        names = []
        values = []
        for note in self.notes:
            if note.name in names:
                raise ValueError(f"Duplicate note name: {note.name}")
            names.append(note.name)
            if note.value in values:
                raise ValueError(f"Duplicate note value: {note.value}")
            values.append(note.value)



@dataclass
class Note:
    """
        A note with a scale for quality control.
        Attributes:
            id: Unique identifier for the note.
            name: Name of the note.
            description: Description of the note.
            scale: Scale used for the note, which can be a NoteScale object.
            value: Value of the note based on the scale.
            comment: Optional comment for additional information.

        Scale can be leaved None if only comment will be used.
    """
    id: str|None = None
    name: str = ""
    description: str = ""
    scale: NoteScale|None = None

    value: int|None = None
    comment: str|None = None

    def __post_init__(self):
        if self.id is None:
            # If not provided, generate an ID from the name
            self.id = self.name.lower().replace(" ", "_")
