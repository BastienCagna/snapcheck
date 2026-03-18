from dataclasses import dataclass, field
from lepton_common.objects import Serializable
from snapcheck.core.renderable import HTMLRenderable
from snapcheck.snap.elements import AbstractElement, list_elements
from snapcheck.snap.rating import Rating


@dataclass
class Board(Serializable, HTMLRenderable):
    title: str = "Untitled Board"
    description: str = ""

    style: dict[str, str] = field(default_factory=dict)  # Board CSS style

    elements: list[AbstractElement] = field(default_factory=list)  # Graphical elements of the board

    @property
    def all_intended_ratings(self) -> list[Rating]:
        """Return the list of all ratings intended by the board elements"""
        ratings = []
        for el in self.elements:
            for r in el.intended_ratings:
                if r not in ratings:
                    ratings.append(r)
        return list(ratings)

    def get_all_elements(self) -> list[AbstractElement]:
        """Return a flat list of all elements in the board, including those in rows."""
        return list_elements(self.elements)

    # HTML Rendering
    def get_html_content(self):
        return self.elements

    def to_html(self, save_path: str | None = None) -> str:
        # Forward additional rendering options (e.g., fill_missing) and ensure title
        html = super().to_html(title=self.title, _style=self.style)

        if save_path is not None:
            with open(save_path, "w") as f:
                f.write(html)
        return html
