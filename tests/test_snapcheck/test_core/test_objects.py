from snapcheck.core.objects import Backupable, Changeable, Serializable


class TestChangeable:

    def test_no_changed_signal_context_manager(self):
        class DummyChangeable(Changeable):
            x: int = 0
        
        res = None

        def clbk(obj):
            nonlocal res
            res = obj.x
            
        dummy = DummyChangeable()
        dummy.has_changed.connect(clbk)
        dummy.x = 10

        assert res == 10

        # Using the context manager to suppress change signals
        with dummy.no_changed_signal():
            dummy.x = 20
            # Inside the context manager, the signal should not be emitted
            assert res == 10

        dummy.x = 30
        # After exiting the context manager, the signal should be emitted again
        assert res == 30


class TestSerializable:
    
    def test_to_dict_basic_attributes(self):
        class DummySerializable(Serializable):
            def __init__(self):
                self.name = "Test"
                self.value = 42
                super().__init__()

        dummy = DummySerializable()
        data = dummy.to_dict()

        assert data["name"] == "Test"
        assert data["value"] == 42
        assert data["__cls__"] == "test_objects.DummySerializable"

    def test_to_dict_nested_serializable(self):
        class NestedSerializable(Serializable):
            def __init__(self):
                self.description = "Nested"
                super().__init__()

        class ParentSerializable(Serializable):
            def __init__(self):
                self.nested = NestedSerializable()
                super().__init__()

        parent = ParentSerializable()
        data = parent.to_dict()

        assert "nested" in data
        assert data["nested"]["description"] == "Nested"
        assert data["nested"]["__cls__"] == "test_objects.NestedSerializable"


class DummyBackupable(Backupable):
    def __init__(self):
        self.attr1 = "value1"
        self.attr2 = 100
        super().__init__()


class TestBackupable:
    def test_backup_and_restore(self):
        dummy = DummyBackupable()

        with dummy.changing():
            dummy.attr1 = "modified"
            dummy.attr2 = 200

        dummy.revert_changes()

        assert dummy.attr1 == "value1"
        assert dummy.attr2 == 100

        dummy.restore_changes()

        assert dummy.attr1 == "modified"
        assert dummy.attr2 == 200

        # Modify attributes after backup
        with dummy.changing():
            dummy.attr1 = "changed again"
            dummy.attr2 = 300

        dummy.revert_changes()
        dummy.revert_changes()

        assert dummy.attr1 == "value1"
        assert dummy.attr2 == 100

        dummy.restore_changes()
        assert dummy.attr2 == 200

        dummy.restore_changes()
        assert dummy.attr2 == 300