from typing import Type, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

# =======================================
# 1. Create
# =======================================

async def insert_data(
    db: AsyncSession,
    data: dict,
    Model: Type[Base]
) -> dict:
    new_data = Model(**data)

    db.add(new_data)
    await db.commit()
    await db.refresh(new_data)

    return new_data

async def insert_batch(
    db: AsyncSession,
    data_list: list,
    Model: Type[Base]
) -> Sequence[Base]:
    data_batch = [Model(**data) for data in data_list]

    db.add_all(data_batch)
    await db.commit()

    for instance in data_batch:
        await db.refresh(instance)

    return data_batch
    