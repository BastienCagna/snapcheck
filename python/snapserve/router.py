from fastapi import APIRouter

import snapserve.qc.contoller as qc

api_router = APIRouter()
api_router.include_router(qc.router, tags=["qc"], prefix="/qc")
