from fastapi import APIRouter

import snapserve.qc.contoller as qc
import snapserve.files.contoller as files

api_router = APIRouter()
api_router.include_router(qc.router, tags=["qc"], prefix="/qc")
api_router.include_router(files.router, tags=["files"], prefix="/f")
