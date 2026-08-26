from typing import Type, Sequence
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base, BaseModel

# =======================================
# 1. Create Data
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
# 2. Read Data
# =======================================
async def get_data_by_id(
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

async def get_all_data(
    db: AsyncSession,
    skip: int,
    limit: int,
    Model: Type[BaseModel]
) -> BaseModel:
    stmt = select(Model).offset(skip).limit(limit)
    result = await db.execute(stmt)


    return result.scalars().all()

# =======================================
# 2. Update Data
# =======================================
async def update_data_with_refresh(
    db: AsyncSession,
    data: dict,
    item_id: uuid.UUID,
    Model: Type[BaseModel]
) -> BaseModel:
    model_data = db.get(Model, item_id)

    for key, value in data.items:
        if hasattr(model_data, key):
            setattr(model_data, key, value)

    await db.commit()
    await db.refresh(model_data)

    return model_data


async def direct_update(
    db: AsyncSession,
    data: dict,
    item_id: uuid.UUID,
    Model: Type[BaseModel]
) -> BaseModel:

    stmt = (
        update(Model)
        .where(Model.id == item_id)
        .values(**data)
        .returning(Model)
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one()

async def delete_data(
    db: AsyncSession,
    item_id: uuid.UUID,
    Model: Type[BaseModel]
) -> uuid.UUID:
    
    stmt = (
        delete(Model)
        .where(Model.id == item_id)
        .returning(Model.id)
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one()
