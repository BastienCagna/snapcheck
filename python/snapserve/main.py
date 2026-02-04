from lepton.app import LeptonApp, LeptonConfig
import snapserve.snap.controller as snap
import snapserve.files.controller as files
import snapserve.content.controller as content

#
app = LeptonApp(
    LeptonConfig(
        
    )
)
app.router.include_router(snap.router, tags=["snap"], prefix="/snap")
app.router.include_router(files.router, tags=["files"], prefix="/files")
app.router.include_router(content.router, tags=["content"], prefix="/content")

if __name__ == "__main__":
    app.start_uvicorn()