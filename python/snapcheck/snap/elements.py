from dataclasses import field
from typing import Iterable, List, Literal, Union
from pydantic import BaseModel
from snapcheck.core.renderable import HTMLRenderable
from snapcheck.snap.annotation import Annotation
from snapcheck.snap.rating import Rating
import shutil
import os.path as op
from warnings import warn


class AbstractElement(BaseModel, HTMLRenderable):
    type: Literal["unknown"] = "unknown"
    title: str | None = None
    style: dict[str, str] = field(default_factory=dict)  # Element CSS style
    intended_ratings: list[Rating] = field(default_factory=list)  # List of rating IDs
    annotations: List[Annotation] = field(default_factory=list)

    def get_html_content(self):
        return "?"
        
    def to_html(self):
        return super().to_html(_style=self.style)


class Element(AbstractElement):
    type: Literal["default"] = "default"
    content: Union[str, "Element", None] = None

    def get_html_content(self) -> str:
        return self.content


class RowElement(Element):
    type: Literal["row"] = "row"
    style: dict = field(default_factory=lambda: {"display": "flex"})
    content: list = field(default_factory=list)

    def __len__(self):
        return len(self.content)

    def __getitem__(self, index):
        return self.content[index]

    def __setitem__(self, index, value):
        self.content[index] = value

    def __delitem__(self, index):
        del self.content[index]

    def __iter__(self):
        return iter(self.content)

    def append(self, item):
        self.content.append(item)

    def extend(self, items):
        self.content.extend(items)

    def insert(self, index, item):
        self.content.insert(index, item)

    def remove(self, item):
        self.content.remove(item)

    def pop(self, index=-1):
        return self.content.pop(index)

    def clear(self):
        self.content.clear()

    def index(self, item, *args):
        return self.content.index(item, *args)

    def count(self, item):
        return self.content.count(item)

    def sort(self, *args, **kwargs):
        self.content.sort(*args, **kwargs)

    def reverse(self):
        self.content.reverse()

    def copy(self):
        return self.content.copy()


class FileElement(AbstractElement):
    type: Literal["file"] = "file"
    is_local: bool = False
    src: str = ""

    def __post_init__(self):
        if not self.is_local:
            # Need to get the full path when initializing the element
            # When the element is alreayd local, keep the relative path
            self.src = op.abspath(self.src)

    def export_to_local(self, root_dir, subdir: str, source_tracker: dict = None):
        """Copy the file to the target directory and update the path.
        Target directory will be created if it does not exist.
        If a file with the same name already exists, a suffix is added.
        If source_tracker is given, avoid to copy several time the same file
        dir_path is attempted to be relative to parent file (like Snap)
        """

        # TODO: add some tests for this function

        if not op.isfile(self.src):
            warn(f"'{self.src}' doest not exist. Cannot export it then replacing with an empty source.")
            self.src = ""

        if self.src != "":
            if source_tracker is not None and self.src in source_tracker:
                self.src = source_tracker[self.src]
            else:
                # Ensure target directory exists
                target_dir = op.join(root_dir, subdir)
                if not op.exists(target_dir):
                    from os import makedirs
                    makedirs(target_dir, exist_ok=True)
                
                fname = op.basename(self.src)
                abs_target = op.join(root_dir, subdir, fname)
                i = 1
                pfx, ext = op.splitext(fname)
                while op.isfile(abs_target):
                    sub_fname = f"{pfx}_{i}{ext}"
                    abs_target = op.join(root_dir, subdir, sub_fname)
                    i += 1
                rel_target = op.relpath(abs_target, root_dir)
                shutil.copy(self.src, abs_target)
                if source_tracker is not None:
                    source_tracker[self.src] = rel_target
                self.src = rel_target
        self.is_local = True


class ImageElement(FileElement):
    type: Literal["image"] = "image"

    def get_html_content(self) -> str:
        return f"<img src='{self.src}' alt='{self.title or ''}' />"


# Union of all element types
ElementUnion = ImageElement | FileElement | RowElement | Element


def list_elements(item: Union[list, ElementUnion]) -> List[ElementUnion]:
    """Recursively list all elements in an element or list of elements."""
    elements = []

    if isinstance(item, AbstractElement):
        elements.append(item)

    if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
        for el in item:
            elements.extend(list_elements(el))
    return elements
