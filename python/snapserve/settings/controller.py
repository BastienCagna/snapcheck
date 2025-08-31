from typing import List
from fastapi import APIRouter, Depends, HTTPException

from snapserve.app_settings import APP_SETTINGS
from snapserve.settings.models import SettingModel, SettingsGroupModel

router = APIRouter()

@router.get("/", response_model=List[SettingsGroupModel])
def get_all_settings():
    return APP_SETTINGS.groups

@router.get("/{path}", response_model=SettingModel)
def get_setting(path: str):
    return APP_SETTINGS.get(path)
