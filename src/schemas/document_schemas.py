from pydantic import BaseModel, Field
from typing import Optional

class DocumentUpload(BaseModel):
    name: str
    description: Optional[str] = Field(
        default=None, description="A synthetized description about the document"
    )
    category: str
    size: int

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = Field(
        default=None, description="A synthetized description about the document"
    )
    category: Optional[str] = None
    size: Optional[int] = None