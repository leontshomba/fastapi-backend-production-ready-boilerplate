from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

# =======================================
# 1. Create
# =======================================

async def insert_data(
    db: AsyncSession,
    # data: dict,
    model: Type[Base]
) -> dict:
    new_data = model

    db.add(new_data)
    await db.commit()
    await db.refresh(new_data)

    return new_data
    