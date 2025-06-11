from dataclasses import dataclass, field
from snapcheck.qc.note import Note


@dataclass
class Element:
    type: str
    title: str|None = None
    style: dict[str, str] = field(default_factory=dict)  # Element CSS style

@dataclass
class ImageElement(Element):
    type: str = "image"
    src: str = ""

@dataclass
class Board:
    title: str
    description: str = ""

    intended_notes: list[Note] = field(default_factory=list) # List of note IDs

    style: dict[str, str] = field(default_factory=dict) # Board CSS style

    elements: list[Element] = field(default_factory=list)  # Graphical elements of the board

    @property
    def __dict__(self):
        return {
            "title": self.title,
            "description": self.description,
            "style": self.style,
            "elements": [element.__dict__ for element in self.elements],
            'intended_notes': [note.id for note in self.intended_notes]
        }