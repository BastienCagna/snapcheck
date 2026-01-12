import pytest
import os
import tempfile
import zipfile
from snapcheck.snap import Snap, load_snap, Board
from snapcheck.snap.elements import ImageElement, Element
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem


class TestSnap:
    def test_create_snap_minimal(self):
        snap = Snap()
        assert snap.title is None
        assert snap.description is None
        assert snap.metadata == {}
        assert snap.ratings == []
        assert snap.boards == []
        assert snap._dir is None
        assert snap._path is None

    def test_create_snap_with_values(self):
        rating = Rating(name="Quality")
        board = Board(title="Test Board")
        
        snap = Snap(
            title="Test Snap",
            description="A test snap",
            metadata={"author": "Test User"},
            ratings=[rating],
            boards=[board]
        )
        
        assert snap.title == "Test Snap"
        assert snap.description == "A test snap"
        assert snap.metadata == {"author": "Test User"}
        assert len(snap.ratings) == 1
        assert len(snap.boards) == 1

    def test_validate_undefined_rating_in_board(self):
        rating1 = Rating(id="rating1", name="Quality")
        rating2 = Rating(id="rating2", name="Accuracy")
        
        element = Element(intended_ratings=[rating2])
        board = Board(title="Board", elements=[element])
        
        # rating2 is used in board but not defined in snap.ratings
        snap = Snap(ratings=[rating1], boards=[board])
        
        with pytest.raises(ValueError, match="is not defined in the ratings list"):
            snap._validate()

    def test_validate_valid_snap(self):
        rating = Rating(id="rating1", name="Quality")
        element = Element(intended_ratings=[rating])
        board = Board(title="Board", elements=[element])
        
        snap = Snap(ratings=[rating], boards=[board])
        snap._validate()  # Should not raise

    def test_validate_checks_scale(self):
        scale = RatingScale(
            description="Scale",
            ratings=[
                RatingScaleItem(name="Good", value=1),
                RatingScaleItem(name="Good", value=2)  # Duplicate name
            ]
        )
        rating = Rating(name="Quality", scale=scale)
        snap = Snap(ratings=[rating])
        
        with pytest.raises(ValueError, match="Duplicate rating name"):
            snap._validate()

    def test_to_dict_without_compress(self):
        rating = Rating(name="Quality")
        board = Board(title="Board")
        snap = Snap(title="Test", ratings=[rating], boards=[board])
        
        data = snap.to_dict(compress=False)
        
        assert data["title"] == "Test"
        assert len(data["ratings"]) == 1
        assert len(data["boards"]) == 1
        assert "_scales" not in data

    def test_to_dict_with_compress(self):
        scale = RatingScale(
            description="Quality scale",
            ratings=[RatingScaleItem(name="Good", value=1)]
        )
        rating1 = Rating(name="Quality1", scale=scale)
        rating2 = Rating(name="Quality2", scale=scale)
        
        snap = Snap(ratings=[rating1, rating2])
        data = snap.to_dict(compress=True)
        
        # Scale should be extracted and referenced
        assert "_scales" in data
        assert len(data["_scales"]) == 1
        assert data["ratings"][0]["scale"].startswith("@._scales#")
        assert data["ratings"][1]["scale"].startswith("@._scales#")

    def test_update_rating(self):
        rating = Rating(id="rating1", name="Quality", value=None)
        snap = Snap(ratings=[rating])
        
        snap.update_rating("rating1", 5)
        
        assert snap.ratings[0].value == 5

    # def test_update_rating_not_found(self):
    #     snap = Snap(ratings=[Rating(id="rating1", name="Quality")])
        
    #     with pytest.raises(ValueError, match="Note with ID 'nonexistent' not found"):
    #         snap.update_rating("nonexistent", 5)

    def test_close(self):
        snap = Snap()
        tmp_dir = tempfile.TemporaryDirectory()
        snap._dir = tmp_dir
        
        dir_path = tmp_dir.name
        assert os.path.exists(dir_path)
        
        snap.close()
        
        # Directory should be cleaned up
        assert not os.path.exists(dir_path)

    # def test_to_json_warning(self):
    #     snap = Snap(title="Test")
        
    #     with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    #         temp_path = f.name
        
    #     try:
    #         with pytest.warns(UserWarning, match="will only save metadata"):
    #             snap.to_json(temp_path)
    #     finally:
    #         if os.path.exists(temp_path):
    #             os.unlink(temp_path)


class TestSnapSaveLoad:
    def test_save_and_load_minimal_snap(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.snap")
            
            # Create and save
            snap = Snap(
                title="Test Snap",
                description="Test description",
                metadata={"version": "1.0"}
            )
            snap.save(save_path)
            
            assert os.path.exists(save_path)
            
            # Load
            loaded_snap = load_snap(save_path)
            
            assert loaded_snap.title == "Test Snap"
            assert loaded_snap.description == "Test description"
            assert loaded_snap.metadata == {"version": "1.0"}
            assert loaded_snap._path == save_path
            
            loaded_snap.close()

    # def test_save_and_load_with_boards_and_ratings(self):
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         save_path = os.path.join(tmpdir, "test.snap")
            
    #         rating = Rating(id="quality", name="Quality")
    #         board = Board(
    #             title="Test Board",
    #             description="Board description"
    #         )
            
    #         snap = Snap(
    #             title="Complex Snap",
    #             ratings=[rating],
    #             boards=[board]
    #         )
    #         snap.save(save_path)
            
    #         loaded_snap = load_snap(save_path)
            
    #         assert loaded_snap.title == "Complex Snap"
    #         assert len(loaded_snap.ratings) == 1
    #         assert loaded_snap.ratings[0].name == "Quality"
    #         assert len(loaded_snap.boards) == 1
    #         assert loaded_snap.boards[0].title == "Test Board"
            
    #         loaded_snap.close()

    def test_save_with_file_elements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test image file
            img_path = os.path.join(tmpdir, "test_image.png")
            with open(img_path, 'wb') as f:
                f.write(b"fake image content")
            
            save_path = os.path.join(tmpdir, "test.snap")
            
            element = ImageElement(src=img_path, is_local=False)
            board = Board(title="Board with image", elements=[element])
            snap = Snap(boards=[board])
            
            snap.save(save_path)
            
            # Verify archive contains content directory
            with zipfile.ZipFile(save_path, 'r') as zf:
                files = zf.namelist()
                assert any('content/' in f for f in files)
            
            # Load and verify
            loaded_snap = load_snap(save_path)
            assert len(loaded_snap.boards) == 1
            assert len(loaded_snap.boards[0].elements) == 1
            
            loaded_snap.close()

    def test_save_without_path_raises_error(self):
        snap = Snap(title="Test")
        
        with pytest.raises(ValueError, match="No path provided"):
            snap.save()

    def test_save_reuses_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.snap")
            
            snap = Snap(title="Test")
            snap.save(save_path)
            
            # Modify and save again without path
            snap.title = "Modified"
            snap.save()
            
            # Should save to same path
            loaded = load_snap(save_path)
            assert loaded.title == "Modified"
            loaded.close()

    def test_load_invalid_archive_no_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create zip without JSON
            zip_path = os.path.join(tmpdir, "invalid.snap")
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("random.txt", "not a json file")
            
            with pytest.raises(FileNotFoundError, match="No JSON file found"):
                load_snap(zip_path)

    # def test_load_validates_snap(self):
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         save_path = os.path.join(tmpdir, "test.snap")
            
    #         # Create snap with invalid reference
    #         rating1 = Rating(id="rating1", name="Quality")
    #         rating2 = Rating(id="rating2", name="Accuracy")
    #         element = Element(intended_ratings=[rating2])
    #         board = Board(title="Board", elements=[element])
            
    #         # Manually save without validation
    #         snap = Snap(ratings=[rating1], boards=[board])
    #         snap.save(save_path)
            
    #         # Loading should fail validation
    #         with pytest.raises(ValueError, match="is not defined in the ratings list"):
    #             load_snap(save_path)
