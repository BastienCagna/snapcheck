import os
# from soma.qt_gui.qt_backend.Qt import QVariant
# from soma.web import WebBackend, json_exception, pyqtSlot
# from populse_db.storage import Storage



# class SnapcheckWebBackend(WebBackend):
#     def __init__(self, database):
#         super().__init__()
#         s = os.path.split(os.path.dirname(__file__)) + ("static",)
#         self.static_path.append("/".join(s))
#         self.database = Storage(database)

#     @pyqtSlot(result=QVariant)
#     @json_exception
#     def global_info(self):
#         with self.database.session() as dbs:
#             return {"data_types": list(dbs.snapshots.distinct_values("data_type"))}
