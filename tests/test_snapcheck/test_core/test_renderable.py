from snapcheck.core.renderable import HTMLRenderable


class TestHTMLRenderable:
    
    def test_default_html_rendering(self):
        renderable = HTMLRenderable()
        html_output = renderable.to_html()
        assert "<html>" in html_output
        assert "<title>Document</title>" in html_output
        assert "</html>" in html_output