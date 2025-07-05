from pydantic import BaseModel
from typing import Any
from datetime import datetime

class EDAResultOut(BaseModel):
    id: int
    upload_id: int
    eda_json: Any
    created_at: datetime

    class Config:
        from_attributes = True