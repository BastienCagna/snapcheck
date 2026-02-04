from fastapi import APIRouter
from lepton.app_data import APP_DATA
from lepton.appdata.models import AppDataModel


router = APIRouter()

@router.get("/", response_model=AppDataModel)
def get_all():
    return APP_DATA.to_dict()
