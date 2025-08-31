from dataclasses import dataclass, field
from typing import Union
from snapcheck.core.objects import Serializable
from snapcheck.snap.rating import Rating
import shutil
import os.path as op
from warnings import warn


@dataclass
class Element:
    type: str = "default"
    title: str|None = None
    style: dict[str, str] = field(default_factory=dict)  # Element CSS style
    content: Union[str, "Element", None] = None

@dataclass
class FileElement(Element):
    is_local: bool = False
    src: str = ""

    def __post_init__(self):
        if not self.is_local:
            # Need to get the full path when initializing the element
            # When the element is alreayd local, keep the relative path
            self.src = op.abspath(self.src)

    def export_to_local(self, dir_path: str, source_tracker: dict=None):
        """ Copy the file to the target directory and update the path.
            Target directory should exist.
            If a file with the same name already exists, a suffix is added.
            If source_tracker is given, avoid to copy several time the same file
            dir_path is attempted to be relative to parent file (like Snap)
        """
        if not op.isfile(self.src):
            warn(f"'{self.src}' doest not exist. Cannot export it then replacing with an empty source.")
            self.src = ""

        if self.src != "":
            if source_tracker is not None and self.src in source_tracker:
                self.src = source_tracker[self.src]
            else:
                fname = op.basename(self.src)
                target = op.join(dir_path, fname)
                i = 1
                while op.isfile(target):
                    pfx, ext = op.splitext(fname)
                    sub_fname = op.join(dir_path, f'{pfx}_{i}{ext}')
                    target = op.join(dir_path, sub_fname)
                shutil.copy(self.src, target)
                if source_tracker is not None:
                    source_tracker[self.src] = target
                self.src = target
        self.is_local = True

@dataclass
class ImageElement(FileElement):
    type: str = "image"

@dataclass
class Board(Serializable):
    title: str
    description: str = ""

    intended_ratings: list[Rating] = field(default_factory=list) # List of rating IDs

    style: dict[str, str] = field(default_factory=dict) # Board CSS style

    elements: list[Element] = field(default_factory=list)  # Graphical elements of the board
