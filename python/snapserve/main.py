from pathlib import Path
from lepton.app import LeptonApp, LeptonConfig
import snapserve.snap.controller as snap
import snapserve.files.controller as files
import snapserve.content.controller as content


config = LeptonConfig(
    app_name="SnapCheck",
    frontend_path=Path(__file__).parent.parent.parent / "snapcheck-front",
    settings_f=Path.home() / ".config/snapcheck/settings.json",
    app_data_f=Path.home() / ".config/snapcheck/app_data.json",
)
#
app = LeptonApp(config)
app.include_router(files.router, tags=["files"], prefix="/files")
app.include_router(content.router, tags=["content"], prefix="/content")
app.include_router(snap.router, tags=["snap"], prefix="/snap")

if __name__ == "__main__":
    app.start_uvicorn()