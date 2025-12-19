import pytest
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem


class TestRatingScaleItem:
    def test_create_rating_scale_item(self):
        item = RatingScaleItem(name="Good", value=1, description="Good quality", color="#00FF00")
        assert item.name == "Good"
        assert item.value == 1
        assert item.description == "Good quality"
        assert item.color == "#00FF00"

    def test_rating_scale_item_defaults(self):
        item = RatingScaleItem(name="", value=0)
        assert item.name == ""
        assert item.value == 0
        assert item.description == ""
        assert item.color is None


class TestRatingScale:
    def test_create_rating_scale(self):
        items = [
            RatingScaleItem(name="Bad", value=0, description="Bad quality", color="#FF0000"),
            RatingScaleItem(name="Good", value=1, description="Good quality", color="#00FF00"),
        ]
        scale = RatingScale(description="Quality scale", ratings=items)
        assert scale.description == "Quality scale"
        assert len(scale.ratings) == 2
        assert scale.ratings[0].name == "Bad"
        assert scale.ratings[1].name == "Good"

    def test_rating_scale_check_duplicate_names(self):
        items = [
            RatingScaleItem(name="Good", value=0),
            RatingScaleItem(name="Good", value=1),
        ]
        scale = RatingScale(description="Quality scale", ratings=items)
        with pytest.raises(ValueError, match="Duplicate rating name: Good"):
            scale.check()

    def test_rating_scale_check_duplicate_values(self):
        items = [
            RatingScaleItem(name="Bad", value=1),
            RatingScaleItem(name="Good", value=1),
        ]
        scale = RatingScale(description="Quality scale", ratings=items)
        with pytest.raises(ValueError, match="Duplicate rating value: 1"):
            scale.check()

    def test_rating_scale_check_valid(self):
        items = [
            RatingScaleItem(name="Bad", value=0),
            RatingScaleItem(name="Good", value=1),
        ]
        scale = RatingScale(description="Quality scale", ratings=items)
        scale.check()  # Should not raise


class TestRating:
    def test_create_rating_with_scale(self):
        scale = RatingScale(
            description="Quality scale",
            ratings=[
                RatingScaleItem(name="Bad", value=0),
                RatingScaleItem(name="Good", value=1),
            ]
        )
        rating = Rating(
            name="Quality",
            description="Quality assessment",
            scale=scale,
            value=1,
            comment="Looks good"
        )
        assert rating.name == "Quality"
        assert rating.description == "Quality assessment"
        assert rating.scale == scale
        assert rating.value == 1
        assert rating.comment == "Looks good"
        assert rating.id == "quality"

    def test_rating_id_generation(self):
        rating = Rating(name="My Rating Name")
        assert rating.id == "my_rating_name"

    def test_rating_with_custom_id(self):
        rating = Rating(id="custom_id", name="My Rating")
        assert rating.id == "custom_id"

    def test_rating_without_scale(self):
        rating = Rating(name="Comment only", comment="Just a comment")
        assert rating.scale is None
        assert rating.value is None
        assert rating.comment == "Just a comment"

    def test_rating_defaults(self):
        rating = Rating()
        assert rating.name == ""
        assert rating.description == ""
        assert rating.scale is None
        assert rating.value is None
        assert rating.comment is None
