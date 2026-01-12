from snapcheck.core.callback import Callback


class TestCallback:

    def test_connect_and_disconnect(self):
        cb = Callback()
        
        res = None

        def set_res(x):
            nonlocal res
            res = x

        cb.connect(set_res)
        for v in [1, "test", [1, 2, 3]]:
            cb.emit(v)
            assert res == v

        cb.disconnect(set_res)

        res = None
        cb.emit(42)
        assert res is None
        
