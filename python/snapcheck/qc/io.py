
from dataclasses import dataclass, field
from typing import Any, List
from snapcheck.core.io import temporarly_change_directory
from snapcheck.core.objects import BSCObject
from snapcheck.qc.board import Board, FileElement
from snapcheck.qc.note import Note
import json
from warnings import warn
import tempfile
import os.path as op
from os import mkdir, rename
import shutil


@dataclass
class QualityControl(BSCObject):
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

    def to_dict(self, validate=False) -> None:
        """ Return the object as dict (optionally after validation) """
        # Validate before saving
        if validate:
            self._validate()
        return super().to_dict()

    def to_json(self, path: str):
        warn(
            "Using to_json() method on QualityControl object will only save metadata.\n" + \
            "To also save the boards content, use the save() method"
        )
        return super().to_json()

    def save(self, path: str):
        # Create the content directory
        fname = op.basename(path).split('.')[-2]
        tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_qc_")
        content_path = op.join(tmp_dir.name, "content")
        mkdir(content_path)
        js_f = op.join(tmp_dir.name, fname + ".json")

        # List all elements
        elements = [element for board in self.boards for element in board.elements if isinstance(element, FileElement)]
        source_tracker = {}
        with temporarly_change_directory(tmp_dir.name):
            # Copy each source file and change its path in each elements
            for el in elements:
                el.export_to_local("./content", source_tracker)

        # Save the JSON file
        super().to_json(js_f)

        # Compress all together
        # TODO: make directly the archive with the proper name
        # Create the archive directly with the desired file name and extension
        base_name, ext = op.splitext(path)
        archive_path = shutil.make_archive(base_name=base_name, format='zip', root_dir=tmp_dir.name)
        # If the extension is not .snapqc, rename the archive
        rename(archive_path, path)


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