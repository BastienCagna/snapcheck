import os
import sys
import types

from populse_db import Storage
from . import SnapcheckWebBackend


def web_server_gui(web_backend):
    import http, http.server
    from soma.web import SomaHTTPHandler

    class Handler(SomaHTTPHandler, web_backend=web_backend):
        pass

    httpd = http.server.HTTPServer(("", 8080), Handler)
    httpd.serve_forever()


def qt_web_gui(web_backend):
    import sys
    from soma.qt_gui.qt_backend import Qt
    from soma.web import SomaBrowserWidget

    s = os.path.split(os.path.dirname(__file__)) + ("static",)
    starting_url = f'file://{"/".join(s)}/index.html'
    app = Qt.QApplication(sys.argv)
    w = SomaBrowserWidget(
        starting_url=starting_url,
        web_backend=web_backend,
    )
    w.show()
    app.exec_()


# TODO: better management of options
options = types.SimpleNamespace(
    web=False,
)
arguments = sys.argv[1:]
if not arguments:
    raise Exception("database path missing")
options.database = arguments.pop(0)

if arguments:
    command = arguments.pop(0)
else:
    command = "view"

error = None
if command in ("view", "web"):
    if arguments:
        error = f"Too many paramaters: {' '.join(arguments)}"
    else:
        if not os.path.exists(options.database):
            raise Exception(f"no such database: {options.database}")
        web_backend = SnapcheckWebBackend(database=options.database)
        if command == "view":
            qt_web_gui(web_backend)
        else:
            web_server_gui(web_backend)
elif command == "create":
    if os.path.exists(options.database):
        raise Exception(f"cannot overwirte file: {options.database}")
    database = Storage(options.database)
    database.add_schema('snapcheck.schema')
    with database.session(write=True) as dbs:
        dbs.snapshots.append(
            {
                "orientation": "axial",
                "top": [1.0, 0.0],
                "size": [2.0, 3.0],
                "dataset": "test",
                "software": "none",
                "time_point": "first",
                "data_type": "a modality",
                "image": "/somewhere/something.png",
                "subject": "john doe",
            }
        )
        dbs.snapshots.append(
            {
                "orientation": "axial",
                "top": [1.0, 0.0],
                "size": [2.0, 3.0],
                "dataset": "test",
                "software": "none",
                "time_point": "second",
                "data_type": "a modality",
                "image": "/somewhere/something.png",
                "subject": "john doe",
            }
        )
        dbs.snapshots.append(
            {
                "orientation": "axial",
                "top": [1.0, 0.0],
                "size": [2.0, 3.0],
                "dataset": "test",
                "software": "none",
                "time_point": "first",
                "data_type": "another modality",
                "image": "/somewhere/something.png",
                "subject": "john doe",
            }
        )
else:
    error = f"unknown command: {command}"
if error:
    raise Exception(error)
