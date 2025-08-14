from fastapi import APIRouter

import snapserve.qc.contoller as qc
import snapserve.files.contoller as files
import snapserve.settings.contoller as settings

api_router = APIRouter()
api_router.include_router(qc.router, tags=["qc"], prefix="/qc")
api_router.include_router(files.router, tags=["files"], prefix="/f")
api_router.include_router(settings.router, tags=["settings"], prefix="/s")
