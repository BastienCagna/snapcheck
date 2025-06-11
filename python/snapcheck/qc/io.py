
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
            for int_note in board.intended_notes:
                for note in self.notes:
                    if int_note.id == note.id:
                        break
                else:
                    raise ValueError(f"Note with #'{note.id}' used by board '{board.title}' is not defined in the notes list.")
        checked_scales = []
        for note in self.notes:
            if note.scale is None or note.scale in checked_scales:
                continue
            note.scale.check()


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

    notes = [Note(**note) for note in data['notes']]

    # Rehydrate the boards with their intended notes
    boards = []
    for board in data['boards']:
        bdata = board
        bnotes = []
        for note_id in bdata.pop('intended_notes', []):
            # Find the note by ID
            for note in notes:
                if note.id == note_id:
                    bnotes.append(note)
                    break
            else:
                raise ValueError(f"Note with ID '{note_id}' not found in loaded notes.")
        bdata['intended_notes'] = bnotes
        boards.append(Board(**bdata ))

    # Convert the loaded data back into a QualityControl object
    qc = QualityControl(
        metadata=data['metadata'],
        notes=notes,
        boards=boards
    )

    # Validate the loaded object
    qc._validate()

    return qc