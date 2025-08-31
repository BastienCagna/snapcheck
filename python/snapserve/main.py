import uvicorn
from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from snapserve.router import api_router
# from sulcilab.database import Base, engine


# Base.metadata.create_all(bind=engine)

def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
app.include_router(api_router) #, prefix=config.API_V1_STR)

origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],#origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# def startup():

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)