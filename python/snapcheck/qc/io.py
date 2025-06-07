
from dataclasses import dataclass, field
from typing import Any, List
from snapcheck.qc.board import Board
from snapcheck.qc.note import Note
import json


@dataclass
class QualityControl:
    title: str|None = None
    description: str|None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    notes: List[Note] = field(default_factory=list)
    boards: List[Board] = field(default_factory=list)

    def _validate(self):
        """
        Check if the QualityControl object is valid.
        This can include checks like ensuring that all notes and boards are properly defined.
        """
        # Check that all notes referenced in boards are defined in the notes list
        for board in self.boards:
            for note_id in board.intended_notes:
                for note in self.notes:
                    if note.id == note_id:
                        break
                else:
                    raise ValueError(f"Note with #'{note_id}' used by board '{board.title}' is not defined in the notes list.")

    def to_json(self, path: str) -> None:
        """ Save as JSON file"""
        # Validate before saving
        self._validate()
        # Write the QualityControl object to a JSON file
        with open(path, 'w') as f:
            json.dump(self, f, default=lambda o: o.__dict__, indent=4)

    def save(self, path: str) -> None:
        """ Save the QualityControl
            This method allows to use an other default serialization method in future.
        """
        self.to_json(path)


def load_quality_control(path: str) -> QualityControl:
    """ Load a QualityControl object from a JSON file """
    with open(path, 'r') as f:
        data = json.load(f)

    # Convert the loaded data back into a QualityControl object
    qc = QualityControl(
        metadata=data['metadata'],
        notes=[Note(**note) for note in data['notes']],
        boards=[Board(**board) for board in data['boards']]
    )

    # Validate the loaded object
    qc._validate()

    return qc