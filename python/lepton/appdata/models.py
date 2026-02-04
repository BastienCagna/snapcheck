from typing import List
from pydantic import BaseModel



class AppDataModel(BaseModel):
    history: List[str]
    