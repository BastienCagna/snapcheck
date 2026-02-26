import json
from os import system
from pathlib import Path
from uuid import uuid4
from lepton_common.objects import IOHelper
import uvicorn
from lepton.session.store import SessionStore
from pydantic import BaseModel
from warnings import warn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends

import lepton.settings.controller as settings
import lepton.appdata.controller as appdata
import lepton.session.controller as session
from lepton.app_data import load_app_data, AppData
from lepton.app_settings import load_settings, Settings
from lepton.auth import Authenticator
import shutil


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


openapi_bin = "node node_modules/openapi-typescript-codegen/bin/index.js"


api_package_json = """
{
  "name": "@lepton/api-client",
  "version": "1.0.0",
  "main": "dist/index.js",
  "module": "./dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "prepare": "npm run build"
  },
  "dependencies": {
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  },
  "files": ["dist"],
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.js"
    }
  }
}


"""

api_ts_config_json = """
{
  "compilerOptions": {
    "target": "ES6",
    "module": "CommonJS",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noImplicitAny": false,
    "strict": false,
    "skipLibCheck": true,
    "lib": ["ES2018", "DOM"]
  },
  "include": ["src/**/*"]
}
"""


def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


def default_router(store: SessionStore, authenticator: Authenticator = None):
    dependencies = []
    if not authenticator:
        warn("Running without authentication.")
    else:
        dependencies.append(Depends(authenticator.verify_token))
    api_router = APIRouter()

    api_router.include_router(
        settings.router,
        tags=["settings"],
        prefix="/settings",
        dependencies=dependencies,
    )
    api_router.include_router(
        appdata.router,
        tags=["appdata"],
        prefix="/appdata",
        dependencies=dependencies,
    )
    api_router.include_router(
        session.CRUDRouter(store), tags=["data"], prefix="/objects", dependencies=dependencies
    )
    api_router.include_router(session.router, tags=["session"], prefix="/session")
    return api_router


class LeptonConfig(BaseModel):
    app_name: str
    # CORS
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    # Build
    frontend_path: str | Path
    api_package_name: str = "@lepton/api-client"
    # Config files
    settings_f: str | Path
    app_data_f: str | Path


class LeptonApp:
    """
    Attributes
    ----------
    config: LeptonConfig
        The config used to initialize the app. Editing this after initialization will not have hazardous effect.
    settings: Settings
        The app settings, loaded from the config.settings_f file.
    app_data: AppData
        The app data, loaded from the config.app_data_f file.
    store: SessionStore
        The session store, used to manage sessions and their items.
    auth: Authenticator
        The authenticator, used to manage authentication and token generation.
    app: FastAPI
        The FastAPI app, used to manage the API and routes.
    data_model: type[BaseModel]
        The Pydantic model repsenting the main data object managed by the app.
    """

    config: LeptonConfig
    settings: Settings
    app_data: AppData
    store: SessionStore
    auth: Authenticator
    app: FastAPI

    def __init__(self, config: LeptonConfig, io_helper: IOHelper):
        """Initialize the app"""
        self.config = config

        # Initialize the session store
        self.store = SessionStore(io_helper)
        self.auth = Authenticator(secret=uuid4().hex)

        # Load settings and app data
        self.settings = load_settings(config.settings_f)
        self.app_data = load_app_data(config.app_data_f)

        # Create the FastAPI app
        self.app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
        # Add the app to the state so that it can be accessed in the controllers
        self.app.state.lepton_app = self

        # Create the default router
        self.router = default_router(self.store, authenticator=self.auth)
        self.app.include_router(self.router)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.allow_origins,
            allow_credentials=config.allow_credentials,
            allow_methods=config.allow_methods,
            allow_headers=config.allow_headers,
        )

    def include_router(self, router: APIRouter, **kwargs):
        """Include a router in the app"""
        self.app.include_router(router, **kwargs)

    def start_uvicorn(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        return uvicorn.run(self.app, host=host, port=port)

    def build_tsx_api(self, build_path: str | Path = None) -> None:
        """Generate the Typescript API client as a package and install it in the frontend"""
        if build_path is None:
            build_path = Path(__file__).parent.parent.parent / "build" / self.config.api_package_name
            # build_path = self.config.frontend_path / "api"

        build_path = Path(build_path)

        if build_path.exists():
            shutil.rmtree(build_path)

        json_f = build_path / "openapi.json"
        build_path.mkdir(parents=True, exist_ok=True)

        print("Exporting the OpenAPI schema specifications")
        with open(json_f, "w+") as afp:
            api = self.app.openapi()
            json.dump(api, afp, indent=4)

        print("Regenerate the Typescript API")
        cmd = "{} --input {} --output {} --client axios".format(openapi_bin, json_f, build_path / "src")
        print(cmd)
        system(cmd)

        package_js = build_path / "package.json"
        with open(package_js, "w+") as pf:
            pf.write(api_package_json)

        tsconfig_js = build_path / "tsconfig.json"
        with open(tsconfig_js, "w+") as tf:
            tf.write(api_ts_config_json)

        # Keep a frontend-local symlink so generated API sources appear under src/lepton.
        frontend_api_link = Path(self.config.frontend_path) / "src" / "lepton" / "api-client"
        frontend_api_link.parent.mkdir(parents=True, exist_ok=True)
        # Replace any previous link/folder before creating the new symlink target.
        if frontend_api_link.is_symlink() or frontend_api_link.is_file():
            frontend_api_link.unlink()
        elif frontend_api_link.exists():
            shutil.rmtree(frontend_api_link)
        frontend_api_link.symlink_to((build_path / "src").resolve(), target_is_directory=True)
        print("Frontend API symlink:", frontend_api_link, "->", (build_path / "src").resolve())

        print("Build path:", build_path)
        print("Frontend path:", self.config.frontend_path)
        system(
            f"cd {build_path}; npm install; npm link; cd {self.config.frontend_path}; npm link {self.config.api_package_name};"
        )
