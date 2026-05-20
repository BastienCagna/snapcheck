from dataclasses import dataclass, field
from typing import Any, List
from os import makedirs, mkdir, rename, listdir
import json
import tempfile
import shutil
import zipfile
from warnings import warn
import os.path as op
from xhtml2pdf import pisa
from pypdf import PdfWriter

from lepton_common import LObject
from snapcheck.snap.board import AbstractElement, Board
from snapcheck.snap.elements import FileElement
from snapcheck.snap.rating import Rating


def html_to_pdf(html_string, output_path):
    with open(output_path, "w+b") as pdf_file:
        pisa.CreatePDF(html_string, dest=pdf_file)


@dataclass
class Snap(LObject):
    title: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    ratings: List[Rating] = field(default_factory=list)
    boards: List[Board] = field(default_factory=list)

    _dir: tempfile.TemporaryDirectory | None = None
    _path: str | None = None

    def get_all_elements(self) -> list[AbstractElement]:
        """Return a flat list of all elements in all boards, including those in rows."""
        all_elements = []
        for board in self.boards:
            all_elements.extend(board.get_all_elements())
        return all_elements

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
                    raise ValueError(
                        f"Rating with #'{rating.id}' used by board '{board.title}' is not defined in the ratings list."
                    )
        checked_scales = []
        for rating in self.ratings:
            if rating.scale is None or rating.scale in checked_scales:
                continue
            rating.scale.check()

    def close(self):
        """Remove temporary directory if set."""
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

    # def _compress(self, data: dict) -> dict:
    #     # List all the scale to save them and use references in ratings
    #     scales = {}
    #     ser_scales = []
    #     for real_rating, ser_rating in zip(self.ratings, data["ratings"]):
    #         if real_rating is None or real_rating.scale is None:
    #             continue
    #         if len(scales) == 0 or real_rating.scale not in scales.values():
    #             id = f"@._scales#{len(scales)}"
    #             scales[id] = real_rating.scale
    #             ser_scales.append(ser_rating["scale"])
    #         else:
    #             for id, scale in scales.items():
    #                 if scale == real_rating.scale:
    #                     break
    #             else:
    #                 raise KeyError(f"Cannot found scale {scale}")
    #         ser_rating["scale"] = id

    #     # Replace intended_ratings of each board to their references
    #     # TODO: do it recursively in elements
    #     for item in data["boards"]:
    #         ref_intended_ratings = []
    #         for el in item["elements"]:
    #             for rating in el["intended_ratings"]:
    #                 rating_id = rating["id"]
    #                 for n, rating in enumerate(data["ratings"]):
    #                     if rating["id"] == rating_id:
    #                         ref_intended_ratings.append(f"@.ratings#{n}")
    #                         break
    #         item["intended_ratings"] = ref_intended_ratings

    #     # List all the ratings to use references (ids) in boards
    #     data["_scales"] = ser_scales

    #     return data

    def to_json(self, path: str):
        warn(
            "Using to_json() method on Snap object will only save metadata.\n"
            + "To also save the boards content, use the save() method"
        )
        return super().to_json()

    def save(self, path: str = None):
        # By default keep the same path
        if path is None:
            if self._filepath is None:
                raise ValueError("No path provided to save the Snap object.")
            path = self._filepath

        # Create the content directory
        fname = op.basename(path).split(".")[-2]
        tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_")
        content_path = op.join(tmp_dir.name, "content")
        mkdir(content_path)
        js_f = op.join(tmp_dir.name, fname + ".json")

        # List all elements
        files_elements: List[FileElement] = list(filter(lambda e: isinstance(e, FileElement), self.get_all_elements()))
        source_tracker = {}
        # Copy each source file and change its path in each elements
        for el in files_elements:
            if el.is_local:
                # If the file is already local, behave as it isn't to
                # copy the files to the new destination
                # It's a bit ugly but it works...
                el.is_local = False
                el.src = op.join(self._dir.name, el.src)
            el.export_to_local(tmp_dir.name, "content", source_tracker)

        # Save the JSON file
        super().to_json(js_f)

        # Compress all together
        # TODO: make directly the archive with the proper name
        # Create the archive directly with the desired file name and extension
        base_name, ext = op.splitext(path)
        archive_path = shutil.make_archive(base_name=base_name, format="zip", root_dir=tmp_dir.name)
        # If the extension is not .snap, rename the archive
        rename(archive_path, path)
        self._filepath = path

        self._has_changed = False

    def export_to_html(self, save_path: str | None = None):
        # Create the ouput directory
        makedirs(save_path, exist_ok=True)

        # Generate boards HTML scripts
        boards = list(board.to_html() for board in self.boards)
        board_links = list(op.join(save_path, f"board_{b}.html") for b in range(len(self.boards)))

        # Header
        header = f"""<div class='snap-header'><div class='snap-title'>{self.title}</div><nav class='snap-nav'><ul>"""
        header += "<li><a href='00_INDEX.html'>Home</a></li>"
        for b, board in enumerate(self.boards):
            header += f"<li><a href='board_{b}.html'>{board.title}</a></li>"
        header += "</ul></nav></div>"

        # Save each board
        for b, board in enumerate(self.boards):
            board_html = f"""<html><head><title>{self.title} - {self.boards[b].title}</title></head><body>"""
            board_html += header
            board_html += boards[b]
            board_html += "</body></html>"
            with open(board_links[b], "w") as f:
                f.write(board_html)

        # Save home page
        home_html = f"""<html><head><title>{self.title}</title></head><body>"""
        home_html += header
        home_html += "<h2>Boards</h2><ul>"
        for b, board in enumerate(self.boards):
            home_html += f"<li><a href='board_{b}.html'>{board.title}</a></li>"
        home_html += "</ul>"
        home_html += "</body></html>"
        home_path = op.join(save_path, "00_INDEX.html")
        with open(home_path, "w") as f:
            f.write(home_html)

        # Copy the content
        ...
        # shutil.copytree(
        #     "./.local/"
        #     dirs_exist_ok=True,
        # )

    def export_to_pdf(self, path: str):
        """Export the Snap object to a PDF file."""
        # Export as HTML in a temporary directory
        tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_pdf_")
        html_dir = op.join(tmp_dir.name, "html")
        self.export_to_html(html_dir)

        # Convert each board HTML to PDF
        pdf_dir = op.join(tmp_dir.name, "pdf")
        makedirs(pdf_dir, exist_ok=True)
        files = []
        for f in sorted(listdir(html_dir)):
            pdf_f = op.join(pdf_dir, f.replace(".html", ".pdf"))
            html_to_pdf(op.join(html_dir, f), pdf_f)
            files.append(pdf_f)

        # Merge all board PDFs into a single PDF file
        merger = PdfWriter()
        for pdf_path in files:
            merger.append(pdf_path)
        merger.write(path)
        merger.close()


def load_snap(path: str) -> Snap:
    """Load a Snap object from a JSON file"""
    tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_load_", delete=False)
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(tmp_dir.name)

    # Find the JSON file at the root of the archive
    json_files = [f for f in listdir(tmp_dir.name) if f.endswith(".json")]
    if not json_files:
        raise FileNotFoundError(f"{path} is an invalid Snap. No JSON file found at the root of the archive.")
    json_path = op.join(tmp_dir.name, json_files[0])
    js_path = json_path

    with open(js_path, "r") as f:
        data = json.load(f)

    snap = Snap.from_dict(data)
    snap._filepath = path
    snap._dir = tmp_dir

    # Validate the loaded object
    snap._validate()

    return snap


def save_snap(snap: Snap, path: str):
    """Save a Snap object to a JSON file"""
    snap.save(path)


def new_snap(path: str) -> Snap:
    """Create a new Snap object with default values."""
    snap = Snap()
    snap._filepath = path
    return snap
