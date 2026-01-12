from typing import List
from snapcheck.core.io import DynamicLoader


class SimpleObject:
    _a: int = 1
    b: str = "text"
    c: List[int] = [1, 2, 3]


class TestDynamicLoader:

    def test_load_class_existing(self):
        loader = DynamicLoader()
        mod = loader.get_module("snapcheck.core.io")
        cls = getattr(mod, "DynamicLoader", None)
        assert mod is not None
        assert cls is not None

    def test_load_class_non_existing(self):
        loader = DynamicLoader()
        try:
            mod = loader.get_module("non.existing.Module")
        except ImportError as e:
            assert "No module named" in str(e)
        else:
            assert False, "Expected ImportError for non-existing class"

    def test_inflate(self):
        loader = DynamicLoader()
        data = {
            "__cls__": "test_io.SimpleObject",
            "_a": 42,
            "b": "hello",
            "c": [4, 5, 6]
        }
        obj = loader.inflate(data)
        assert isinstance(obj, SimpleObject)
        assert obj._a == 42
        assert obj.b == "hello"
        assert obj.c == [4, 5, 6]