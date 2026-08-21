from typing import Type, Sequence
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base, BaseModel

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

# =======================================
# 2. Read
# =======================================
async def read_by_id(
    db: AsyncSession,
    data_id: uuid.UUID,
    Model: Type[BaseModel]
) -> BaseModel:
    stmt = select(Model).where(Model.id == data_id)
    result = await db.execute(stmt)

    data = result.scalar_one_or_none()

    if data is None:
        print(f"No data with the id '{data_id}' in table: {Model}")
        
        return None

    return data