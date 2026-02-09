from fastapi import APIRouter
from lepton.appdata.models import AppDataModel


router = APIRouter()

@router.get("/", response_model=AppDataModel)
def get_all():
    raise NotImplementedError("Not implemented yet")
