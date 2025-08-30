from typing import List
from pydantic import BaseModel
from snapcheck.core.objects import Serializable



class ContentModel(BaseModel):
    path: str
    content: str

