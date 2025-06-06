from dataclasses import dataclass, field


@dataclass
class NoteScale:
    description: str = ""
    notes: dict[int, str] = field(default_factory=dict)


@dataclass
class Note:
    id: str|None = None
    name: str = ""
    description: str = ""
    scale: NoteScale|None = None

    value: int|None = None
    comment: str|None = None

    def __post_init__(self):
        if self.id is None:
            self.id = self.name.lower().replace(" ", "_")