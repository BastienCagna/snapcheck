from fastapi import APIRouter

import snapserve.snap.contoller as snap
import snapserve.files.contoller as files
import snapserve.settings.contoller as settings
import snapserve.content.contoller as content

api_router = APIRouter()
api_router.include_router(snap.router, tags=["snap"], prefix="/snap")
api_router.include_router(files.router, tags=["files"], prefix="/files")
api_router.include_router(settings.router, tags=["settings"], prefix="/settings")
api_router.include_router(content.router, tags=["content"], prefix="/content")
