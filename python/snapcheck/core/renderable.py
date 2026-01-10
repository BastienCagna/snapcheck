from dataclasses import dataclass
from typing import Iterable, Any


@dataclass
class HTMLRenderable:
    """Mixin class to provide HTML rendering capability."""
    
    def get_html_content(self) -> Any:
        """Provide the content to be rendered inside the HTML element."""
        return ""

    def to_html(self, _style=None, _classes=None, _id=None, _template=None, **kwargs) -> str:
        """Generate an HTML representation of the element."""
        html = "<div"
        if _id:
            html += f" id='{self.html_id}'"
        if _classes:
            html += f" class=\"{' '.join(self.html_classes)}\""
        if _style:
            style_str = "; ".join(f"{k}: {v}" for k, v in self.html_style.items())
            html += f" style=\"{style_str}\""
        html += ">"
        content = self.get_html_content()
        if isinstance(content, HTMLRenderable):
            content = content.to_html()
        elif isinstance(content, Iterable) and not isinstance(content, str):
            content = "".join(
                item.to_html() if isinstance(item, HTMLRenderable) else str(item)
                for item in content
            )

        return html + content + "</div>"