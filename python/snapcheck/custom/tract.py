from typing import Literal
from snapcheck.snap.elements import FileElement


class TractElement(FileElement):
    type: Literal["tract"] = "tract"

    def get_html_content(self) -> str:
        return "<div class='viewer-3d' />"
