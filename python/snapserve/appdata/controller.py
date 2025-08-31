from typing import List
from fastapi import APIRouter, Depends, HTTPException
from snapserve.app_data import APP_DATA
from snapserve.appdata.models import AppDataModel


router = APIRouter()

@router.get("/", response_model=AppDataModel)
def get_all():
    return APP_DATA.to_dict()
