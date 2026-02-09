from typing import List
from fastapi import APIRouter, Request

from fastapi.params import Depends
from lepton.settings.models import SettingModel, SettingsGroupModel


def get_lepton_app(request: Request):
    return request.app.state.lepton_app

router = APIRouter()

@router.get("/", response_model=List[SettingsGroupModel])
def get_all_settings(lepton = Depends(get_lepton_app)):
    return lepton.settings.groups

@router.get("/{path}", response_model=SettingModel)
def get_setting(path: str, lepton = Depends(get_lepton_app)):
    return lepton.settings.get(path)