from typing import Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import BaseModel

class Document(BaseModel):
    __tablename__="documents"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(Integer)