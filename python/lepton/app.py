import json
from os import system
from pathlib import Path
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
from lepton.app_data import load_app_data, AppData
from lepton.app_settings import load_settings, Settings
from lepton.auth import verify_token
import shutil


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


def default_router(unsafe=False):
    dependencies = []
    if unsafe:
        warn("Running in unsafe mode.")
    else:
        dependencies.append(Depends(verify_token))
    api_router = APIRouter(dependencies=dependencies)

    api_router.include_router(settings.router, tags=["settings"], prefix="/lpt/settings")
    api_router.include_router(appdata.router, tags=["appdata"], prefix="/lpt/appdata")
    return api_router


# @app.on_event("startup")
# def startup():


class LeptonConfig(BaseModel):
    app_name: str
    # Debug
    unsafe_mode: bool = False
    # CORS
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    # Build
    frontend_path: str | Path
    # Config files
    settings_f: str | Path
    app_data_f: str | Path


class LeptonApp:
    config: LeptonConfig
    settings: Settings
    app_data: AppData
    store: SessionStore
    app: FastAPI

    def __init__(self, config: LeptonConfig):
        """Initialize the app"""
        self.config = config

        # Initialize the session store
        self.store = SessionStore()

        # Load settings and app data
        self.settings = load_settings(config.settings_f)
        self.app_data = load_app_data(config.app_data_f)

        # Create the FastAPI app
        self.app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
        
        # Create the default router
        self.router = default_router(unsafe=config.unsafe_mode)
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

    def start_uvicorn(self):
        return uvicorn.run(self.app, host=self.config.host, port=self.config.port)

    def build_tsx_api(self, build_path: str | Path = None) -> None:
        """Generate the Typescript API client"""
        if build_path is None:
            build_path = Path(__file__).parent.parent.parent / "build" / "@lepton/api_client"
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
        cmd = "{} --input {} --output {} --client axios".format(
            openapi_bin, json_f, build_path / "src"
        )
        print(cmd)
        system(cmd)

        package_js = build_path / "package.json"
        with open(package_js, "w+") as pf:
            pf.write(api_package_json)

        tsconfig_js = build_path / "tsconfig.json"
        with open(tsconfig_js, "w+") as tf:
            tf.write(api_ts_config_json)

        print("Build path:", build_path)
        print("Frontend path:", self.config.frontend_path)
        system(f"cd {build_path}; npm install; npm link; cd {self.config.frontend_path}; npm link @lepton/api-client")
