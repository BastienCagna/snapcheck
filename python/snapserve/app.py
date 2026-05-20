from pathlib import Path
from lepton.app import LeptonApp, LeptonConfig
from lepton_common.objects import IOHelper

from snapcheck.snap import load_snap, save_snap, new_snap
import snapserve.snap.controller as snap
import snapserve.files.controller as files
import snapserve.content.controller as content
from snapserve.snap.models import SnapModel


config = LeptonConfig(
    app_name="SnapCheck",
    frontend_path=Path(__file__).parent.parent.parent / "snapcheck-front",
    config_dir=Path.home() / ".config/snapcheck",
)

app = LeptonApp(config, IOHelper(SnapModel, load_snap, save_snap, new_snap))
app.include_router(files.router, tags=["files"], prefix="/files")
app.include_router(content.router, tags=["content"], prefix="/content")
app.include_router(snap.router, tags=["snap"], prefix="/snap")


