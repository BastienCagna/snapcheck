from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials

from lepton.auth import TokenData, bearer_scheme
from lepton.core.utils import get_lepton_app
from pydantic import BaseModel

from lepton.session.models import SessionModel


import typing

if typing.TYPE_CHECKING:
    from lepton.app import LeptonApp


router = APIRouter()


async def get_token_data(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    lepton: "LeptonApp" = Depends(get_lepton_app),
):
    return await lepton.auth.verify_token(credentials)


def get_session_from_token(
    token_data: TokenData = Depends(get_token_data),
    lepton: "LeptonApp" = Depends(get_lepton_app),
):
    if not token_data.sid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session id in token",
        )
    try:
        return lepton.store.get_session(token_data.sid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found",
        )


@router.post("/", response_model=str)
def create_session(lepton: "LeptonApp" = Depends(get_lepton_app)):
    session = lepton.store.new_session()
    return lepton.auth.create_access_token(TokenData(sid=session.id))


@router.delete("/", response_model=None)
def close_session(
    session=Depends(get_session_from_token),
    lepton: "LeptonApp" = Depends(get_lepton_app),
):
    items = lepton.store.close_session(session.id)
    if items:
        return None
    return None


@router.get("/", response_model=SessionModel)
def get_session_infos(session=Depends(get_session_from_token)):
    return session


# @router.get("/saveall")
# def save_all_objects(session=Depends(get_session_from_token)):
#     for item in session.items:
#         item.save()
#     return None


def list_objects(session=Depends(get_session_from_token)):
    return [item.to_dict(clean=True) for item in session.items]


def get_one_by(session=Depends(get_session_from_token), by: str = "id", value: str = ""):
    for item in session.items:
        if getattr(item, by, None) == value:
            return item.to_dict(clean=True)
    raise HTTPException(status_code=404, detail="Item not found")


class CRUDRouter(APIRouter):
    def __init__(self, data_model: type[BaseModel]):
        super().__init__()
        self.data_model = data_model

        # List objects
        self.add_api_route("/all", list_objects, methods=["GET"], response_model=list[self.data_model])
        # Get one object by id
        self.add_api_route("/{value}", get_one_by, methods=["GET"], response_model=self.data_model)
        # Get one object by any attribute
        self.add_api_route("/one/{by}/{value}", get_one_by, methods=["GET"], response_model=self.data_model)
        # Load
        # Create object
        # Update object
        # Delete object
