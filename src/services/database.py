from typing import Type, Sequence
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base, BaseModel


class DatabaseService():

    def __init__(self, db_session: AsyncSession):
        self.db: AsyncSession = db_session


    # =======================================
    # 1. Create Data
    # =======================================
    async def insert_data(
        self,
        data: dict,
        Model: Type[Base]
    ) -> dict:
        new_data = Model(**data)

        self.db.add(new_data)
        await self.db.commit()
        await self.db.refresh(new_data)

        return new_data


    async def insert_batch(
        self,
        data_list: list,
        Model: Type[Base]
    ) -> Sequence[Base]:
        data_batch = [Model(**data) for data in data_list]

        self.db.add_all(data_batch)
        await self.db.commit()

        for instance in data_batch:
            await self.db.refresh(instance)

        return data_batch

    # =======================================
    # 2. Read Data
    # =======================================
    async def get_data_by_id(
        self,
        data_id: uuid.UUID,
        Model: Type[BaseModel]
    ) -> BaseModel:
        stmt = select(Model).where(Model.id == data_id)
        result = await self.db.execute(stmt)

        data = result.scalar_one_or_none()

        if data is None:
            print(f"No data with the id '{data_id}' in table: {Model}")

            return None

        return data


    async def get_all_data(
        self,
        skip: int,
        limit: int,
        Model: Type[BaseModel]
    ) -> BaseModel:
        stmt = select(Model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)

        return result.scalars().all()

    # =======================================
    # 2. Update Data
    # =======================================
    async def direct_update(
        self,
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

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.scalar_one()


    async def update_data_with_refresh(
        self,
        data: dict,
        item_id: uuid.UUID,
        Model: Type[BaseModel]
    ) -> BaseModel:
        model_data = self.db.get(Model, item_id)

        for key, value in data.items:
            if hasattr(model_data, key):
                setattr(model_data, key, value)

        await self.db.commit()
        await self.db.refresh(model_data)

        return model_data

    # =======================================
    # 4. Delete Data
    # =======================================
    async def delete_data(
        self,
        item_id: uuid.UUID,
        Model: Type[BaseModel]
    ) -> uuid.UUID:
        
        stmt = (
            delete(Model)
            .where(Model.id == item_id)
            .returning(Model.id)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.scalar_one()
