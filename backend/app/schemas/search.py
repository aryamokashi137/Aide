from pydantic import BaseModel
from typing import Optional

class GlobalSearchResult(BaseModel):
    id: int
    name: str
    type: str # 'college', 'school', 'pg', etc.
    category: str # 'Education', 'Stay', 'Medical'
    image: Optional[str] = None

    class ConfigDict:
        from_attributes = True
