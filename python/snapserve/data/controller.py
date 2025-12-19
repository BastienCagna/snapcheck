from typing import List
from fastapi import APIRouter, Depends, HTTPException

from snapserve.app_data import APP_DATA
from snapserve.settings.models import SettingModel, SettingsGroupModel
from typing import Any

router = APIRouter()

@router.get("/{key}", response_model=Any)
def get(key: str):
    try:
        return APP_DATA.get(key)
    except KeyError:
        raise HTTPException(status_code=404, detail="Setting not found")

@router.get("/{path}", response_model=SettingModel)
def set(path: str, value: Any):
    APP_DATA.set(path, value)