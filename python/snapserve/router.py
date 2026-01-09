from os import getenv
from warnings import warn
from fastapi import APIRouter, Depends

import snapserve.snap.controller as snap
import snapserve.files.controller as files
import snapserve.settings.controller as settings
import snapserve.content.controller as content
import snapserve.appdata.controller as appdata
from snapserve.auth import verify_token

# Use set SNAP_UNSAFE to disable token verification (used for debug)
unsafe_mode = getenv("SNAP_UNSAFE", False)
if unsafe_mode:
    warn("Running in unsafe mode.")
    api_router = APIRouter()
else:
    api_router = APIRouter(dependencies=[Depends(verify_token)])

api_router.include_router(snap.router, tags=["snap"], prefix="/snap")
api_router.include_router(files.router, tags=["files"], prefix="/files")
api_router.include_router(settings.router, tags=["settings"], prefix="/settings")
api_router.include_router(content.router, tags=["content"], prefix="/content")
api_router.include_router(appdata.router, tags=["appdata"], prefix="/appdata")
