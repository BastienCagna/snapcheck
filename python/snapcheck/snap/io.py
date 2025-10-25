
from dataclasses import dataclass, field
from typing import Any, List
from snapcheck.core.io import temporarly_change_directory
from snapcheck.core.objects import BSCObject
from snapcheck.snap.board import Board, FileElement
from snapcheck.snap.rating import Rating
import json
from warnings import warn
import tempfile
import os.path as op
from os import mkdir, rename, listdir
import shutil
import zipfile


@dataclass
class Snap(BSCObject):
    title: str|None = None
    description: str|None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    ratings: List[Rating] = field(default_factory=list)
    boards: List[Board] = field(default_factory=list)

    _dir: tempfile.TemporaryDirectory|None = None
    _path: str|None = None

    def _validate(self):
        """
        Check if the Snap object is valid.
        This can include checks like ensuring that all ratings and boards are properly defined.
        """
        # Check that all ratings referenced in boards are defined in the ratings list
        for board in self.boards:
            for int_rating in board.all_intended_ratings:
                for rating in self.ratings:
                    if int_rating.id == rating.id:
                        break
                else:
                    raise ValueError(f"Rating with #'{rating.id}' used by board '{board.title}' is not defined in the ratings list.")
        checked_scales = []
        for rating in self.ratings:
            if rating.scale is None or rating.scale in checked_scales:
                continue
            rating.scale.check()

    def to_dict(self, validate=False, compress=True) -> None:
        """ Return the object as dict (optionally after validation) """
        # Validate before saving
        if validate:
            self._validate()

        data = super().to_dict()

        if not compress:
            return data

        # List all the scale to save them and use references in ratings
        scales = {}
        ser_scales = []
        for real_rating, ser_rating in zip(self.ratings, data["ratings"]):
            if real_rating is None or real_rating.scale is None:
                continue
            if len(scales) == 0 or real_rating.scale not in scales.values():
                id = f"@._scales#{len(scales)}"
                scales[id] = real_rating.scale
                ser_scales.append(ser_rating["scale"])
            else:
                for id, scale in scales.items():
                    if scale == real_rating.scale:
                        break
                else:
                    raise KeyError(f"Cannot found scale {scale}")
            ser_rating["scale"] = id

        # Replace intended_ratings of each board to their references
        # TODO: use elements intended_ratings!
        for item in data["boards"]:
            ref_intended_ratings = []
            for rating in item["intended_ratings"]:
                rating_id = rating["id"]
                for n, rating in enumerate(data["ratings"]):
                    if rating["id"] == rating_id:
                        ref_intended_ratings.append(f"@.ratings#{n}")
                        break
            item["intended_ratings"] = ref_intended_ratings

        # List all the ratings to use references (ids) in boards
        data["_scales"] = ser_scales

        return data

    def to_json(self, path: str):
        warn(
            "Using to_json() method on Snap object will only save metadata.\n" + \
            "To also save the boards content, use the save() method"
        )
        return super().to_json()

    def save(self, path: str = None):
        # By default keep the same path
        if path is None:
            if self._path is None:
                raise ValueError("No path provided to save the Snap object.") 
            path = self._path

        # Create the content directory
        fname = op.basename(path).split('.')[-2]
        tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_")
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
        # If the extension is not .snap, rename the archive
        rename(archive_path, path)
        self._path = path

    def close(self):
        """Remove temporary directory if set. """
        if self._dir:
            self._dir.cleanup()


    def update_rating(self, ratingId: str, value: any):
        with self.changing():
            for i, n in enumerate(self.ratings):
                if n.id == ratingId:
                    self.ratings[i].value = value
                    break
            else:
                raise ValueError(f"Note with ID '{ratingId}' not found.")

def load_snap(path: str) -> Snap:
    """ Load a Snap object from a JSON file """
    tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_load_", delete=False)
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir.name)

    # Find the JSON file at the root of the archive
    json_files = [f for f in listdir(tmp_dir.name) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError("No JSON file found at the root of the archive.")
    json_path = op.join(tmp_dir.name, json_files[0])
    js_path = json_path

    with open(js_path, 'r') as f:
        data = json.load(f)

    snap = Snap.from_dict(data)
    snap._path = path
    del snap._scales
    snap._dir = tmp_dir

    # Validate the loaded object
    snap._validate()

    return snap