from dataclasses import dataclass, field


@dataclass
class Element:
    component: str
    props: dict[str, str] = field(default_factory=dict)  # Component properties
    style: dict[str, str] = field(default_factory=dict)  # Element CSS style

@dataclass
class Board:
    title: str
    description: str = ""

    intended_notes: list[str] = field(default_factory=list) # List of note IDs

    style: dict[str, str] = field(default_factory=dict) # Board CSS style

    elements: list[Element] = field(default_factory=list)  # Graphical elements of the board
