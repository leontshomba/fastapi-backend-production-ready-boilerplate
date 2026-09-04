from pydantic import BaseModel, Field
from typing import Optional

class DocumentUpload(BaseModel):
    name: str
    description: Optional[str] = Field(
        default="", description="A synthetized description about the document"
    )
    category: str
    size: int