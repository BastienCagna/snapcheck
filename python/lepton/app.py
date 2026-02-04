import uvicorn
from lepton.session import SessionStore
from pydantic import BaseModel
from warnings import warn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends

import lepton.settings.controller as settings
import lepton.appdata.controller as appdata
from lepton.auth import verify_token


def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


def default_router(unsafe=False):
    if unsafe:
        warn("Running in unsafe mode.")
        api_router = APIRouter()
    else:
        api_router = APIRouter(dependencies=[Depends(verify_token)])

    api_router.include_router(settings.router, tags=["settings"], prefix="/lpt/settings")
    api_router.include_router(appdata.router, tags=["appdata"], prefix="/lpt/appdata")
    return api_router


# @app.on_event("startup")
# def startup():

class LeptonConfig(BaseModel):
    unsafe_mode: bool = False
    allow_origins: list[str] = ["*"]
    host: str = "127.0.0.1"
    port: int = 8000



class LeptonApp:
    config: LeptonConfig
    store: SessionStore
    app: FastAPI
    router: APIRouter

    def __init__(self, config: LeptonConfig = LeptonConfig()):
        """ Initialize the app """
        self.config = config

        # Initialize the session store
        self.store = SessionStore()

        # Create the FastAPI app
        self.app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
        # Create the default router
        self.router = default_router(unsafe=config.unsafe_mode)
        self.app.include_router(self.router)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        

    def start_uvicorn(self):
        return uvicorn.run(self.app, host=self.config.host, port=self.config.port)