from fastapi import APIRouter
from fastapi.params import Depends
from lepton.appdata.models import AppDataModel
from lepton.utils import get_lepton_app


router = APIRouter()


@router.get("/", response_model=AppDataModel)
def get_all(lepton=Depends(get_lepton_app)):
    return lepton.app_data
