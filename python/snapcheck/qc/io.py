
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
from os import mkdir, rename, listdir
import shutil
import zipfile


@dataclass
class QualityControl(BSCObject):
    title: str|None = None
    description: str|None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    notes: List[Note] = field(default_factory=list)
    boards: List[Board] = field(default_factory=list)

    _dir: tempfile.TemporaryDirectory|None = None

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

    def to_dict(self, validate=False, factorize=True) -> None:
        """ Return the object as dict (optionally after validation) """
        # Validate before saving
        if validate:
            self._validate()

        data = super().to_dict()

        if not factorize:
            return data

        # List all the scale to save them and use references in notes
        scales = {}
        ser_scales = []
        for real_note, ser_note in zip(self.notes, data["notes"]):
            if real_note is None or real_note.scale is None:
                continue
            if len(scales) == 0 or real_note.scale not in scales.values():
                id = f"@._scales#{len(scales)}"
                scales[id] = real_note.scale
                ser_scales.append(ser_note["scale"])
            else:
                for id, scale in scales.items():
                    if scale == real_note.scale:
                        break
                else:
                    raise KeyError(f"Cannot found scale {scale}")
            ser_note["scale"] = id

        # Replace intended_notes of each board to their references
        for item in data["boards"]:
            ref_intended_notes = []
            for note_id in item["intended_notes"]:
                for n, note in enumerate(data["notes"]):
                    if note["id"] == note_id:
                        ref_intended_notes.append(f"@.notes#{n}")
                        break
            item["intended_notes"] = ref_intended_notes                        

        # List all the notes to use references (ids) in boards
        data["_scales"] = ser_scales

        return data

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

    def close(self):
        """Remove temporary directory if set. """
        if self._dir:
            self._dir.cleanup()


def load_quality_control(path: str) -> QualityControl:
    """ Load a QualityControl object from a JSON file """
    tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_qc_load_", delete=False)
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir.name)

    # Find the JSON file at the root of the archive
    json_files = [f for f in listdir(tmp_dir.name) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError("No JSON file found at the root of the archive.")
    json_path = op.join(tmp_dir.name, json_files[0])
    path = json_path

    with open(path, 'r') as f:
        data = json.load(f)
    # notes = [Note(**note) for note in data['notes']]

    # # Rehydrate the boards with their intended notes
    # boards = []
    # for board in data['boards']:
    #     bdata = board
    #     bnotes = []
    #     for note_id in bdata.pop('intended_notes', []):
    #         # Find the note by ID
    #         for note in notes:
    #             if note.id == note_id:
    #                 bnotes.append(note)
    #                 break
    #         else:
    #             raise ValueError(f"Note with ID '{note_id}' not found in loaded notes.")
    #     bdata['intended_notes'] = bnotes
    #     boards.append(Board(**bdata ))

    # Convert the loaded data back into a QualityControl object
    # qc = QualityControl(
    #     metadata=data['metadata'],
    #     notes=notes,
    #     boards=boards
    # )

    qc = QualityControl.from_dict(data)
    del qc._scales
    qc._dir = tmp_dir

    # Validate the loaded object
    qc._validate()

    return qc