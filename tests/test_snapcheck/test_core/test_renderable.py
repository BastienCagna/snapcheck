from snapcheck.core.renderable import HTMLRenderable


class TestHTMLRenderable:
    
    def test_default_html_rendering(self):
        renderable = HTMLRenderable()
        html_output = renderable.to_html()
        assert "<div>" in html_output
        assert "</div>" in html_output