import pytest
import os
import tempfile
from snapcheck.snap.elements import Element, FileElement, ImageElement
from snapcheck.snap.board import Board
from snapcheck.snap.rating import Rating
from snapcheck.snap.annotation import Annotation


class TestElement:
    def test_create_element_default(self):
        element = Element()
        assert element.type == "default"
        assert element.title is None
        assert element.style == {}
        assert element.content is None
        assert element.intended_ratings == []
        assert element.annotations == []

    def test_create_element_with_values(self):
        rating = Rating(name="Quality", description="Quality rating")
        annotation = Annotation()
        element = Element(
            title="Test Element",
            style={"color": "red"},
            content="Test content",
            intended_ratings=[rating],
            annotations=[annotation]
        )
        assert element.type == "default"
        assert element.title == "Test Element"
        assert element.style == {"color": "red"}
        assert element.content == "Test content"
        assert len(element.intended_ratings) == 1
        assert len(element.annotations) == 1

    def test_element_nested_content(self):
        nested = Element(content="inner")
        parent = Element(content=nested)
        assert parent.content.type == "default"
        assert parent.content.content == "inner"


class TestFileElement:
    def test_create_file_element_local(self):
        element = FileElement(is_local=True, src="relative/path.txt")
        assert element.is_local is True
        assert element.src == "relative/path.txt"

    def test_create_file_element_absolute_path(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        temp_file.close()
        try:
            element = FileElement(is_local=False, src=temp_file.name)
            assert element.is_local is False
            assert os.path.isabs(element.src)
            assert element.src == os.path.abspath(temp_file.name)
        finally:
            os.unlink(temp_file.name)

    def test_export_to_local_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            element = FileElement(src="/nonexistent/file.txt", is_local=False)
            with pytest.warns(UserWarning, match="doest not exist"):
                element.export_to_local(tmpdir, "content")
            assert element.src == ""
            assert element.is_local is True

    def test_export_to_local_copy_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file
            src_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            src_file.write(b"test content")
            src_file.close()
            
            try:
                element = FileElement(src=src_file.name, is_local=False)
                element.export_to_local(tmpdir, "content")
                
                assert element.is_local is True
                assert "content" in element.src
                full_path = os.path.join(tmpdir, element.src)
                assert os.path.isfile(full_path)
                
                # Verify content was copied
                with open(full_path, 'rb') as f:
                    assert f.read() == b"test content"
            finally:
                os.unlink(src_file.name)

    def test_export_to_local_with_name_conflict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file
            src_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir=tmpdir)
            src_file.write(b"original")
            src_file.close()
            basename = os.path.basename(src_file.name)
            
            # Create conflicting file in target content directory
            content_dir = os.path.join(tmpdir, "content")
            os.makedirs(content_dir, exist_ok=True)
            conflict_path = os.path.join(content_dir, basename)
            with open(conflict_path, 'w') as f:
                f.write("conflict")
            
            try:
                element = FileElement(src=src_file.name, is_local=False)
                element.export_to_local(tmpdir, "content")
                
                # Should have suffix added due to conflict
                assert element.is_local is True
                assert os.path.basename(element.src) != basename
                assert "_1" in os.path.basename(element.src)
            finally:
                os.unlink(src_file.name)

    def test_export_to_local_with_source_tracker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            src_file.write(b"tracked")
            src_file.close()
            
            try:
                tracker = {}
                element1 = FileElement(src=src_file.name, is_local=False)
                element1.export_to_local(tmpdir, "content", source_tracker=tracker)
                
                # Second element with same source should reuse path
                element2 = FileElement(src=src_file.name, is_local=False)
                element2.export_to_local(tmpdir, "content", source_tracker=tracker)
                
                assert element1.src == element2.src
                assert src_file.name in tracker
                assert tracker[src_file.name] == element1.src
            finally:
                os.unlink(src_file.name)


class TestImageElement:
    def test_create_image_element(self):
        element = ImageElement(src="/path/to/image.png")
        assert element.type == "image"
        assert element.src == os.path.abspath("/path/to/image.png")

    def test_image_element_inherits_file_element(self):
        element = ImageElement()
        assert isinstance(element, FileElement)


class TestBoard:
    def test_create_board_minimal(self):
        board = Board(title="Test Board")
        assert board.title == "Test Board"
        assert board.description == ""
        assert board.style == {}
        assert board.elements == []

    def test_create_board_with_elements(self):
        element1 = Element()
        element2 = ImageElement(src="/path/to/image.png", is_local=True)
        
        board = Board(
            title="Board with elements",
            description="Test description",
            style={"background": "white"},
            elements=[element1, element2]
        )
        
        assert board.title == "Board with elements"
        assert board.description == "Test description"
        assert board.style == {"background": "white"}
        assert len(board.elements) == 2

    def test_all_intended_ratings_empty(self):
        board = Board(title="Empty Board")
        assert board.all_intended_ratings == []

    def test_all_intended_ratings_single_element(self):
        rating1 = Rating(name="Quality")
        rating2 = Rating(name="Accuracy")
        element = Element(intended_ratings=[rating1, rating2])
        board = Board(title="Board", elements=[element])
        
        ratings = board.all_intended_ratings
        assert len(ratings) == 2
        assert rating1 in ratings
        assert rating2 in ratings

    def test_all_intended_ratings_multiple_elements(self):
        rating1 = Rating(name="Quality")
        rating2 = Rating(name="Accuracy")
        rating3 = Rating(name="Completeness")
        
        element1 = Element(intended_ratings=[rating1, rating2])
        element2 = Element(intended_ratings=[rating2, rating3])
        
        board = Board(title="Board", elements=[element1, element2])
        
        ratings = board.all_intended_ratings
        assert len(ratings) == 3
        assert rating1 in ratings
        assert rating2 in ratings
        assert rating3 in ratings

    def test_all_intended_ratings_deduplicates(self):
        rating = Rating(name="Quality")
        element1 = Element(intended_ratings=[rating])
        element2 = Element(intended_ratings=[rating])
        
        board = Board(title="Board", elements=[element1, element2])
        
        ratings = board.all_intended_ratings
        # Should not duplicate the same rating instance
        assert len(ratings) == 1
        assert rating in ratings

    def test_board_is_serializable(self):
        from snapcheck.core.objects import Serializable
        board = Board(title="Test")
        assert isinstance(board, Serializable)
