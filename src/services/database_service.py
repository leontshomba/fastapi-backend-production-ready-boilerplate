from typing import TypeVar, Type, Sequence, Optional
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

T = TypeVar("T", bound=Base)

class DatabaseService():

    def __init__(self, db_session: AsyncSession):
        self.db: AsyncSession = db_session


    async def save(self):
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            print(f"Database commit failed: {e}")
            raise


    # =======================================
    # 1. Create Data
    # =======================================
    async def insert_data(
        self,
        Model: Type[T],
        data: dict,
    ) -> T:
        instance = Model(**data)

        self.db.add(instance)
        await self.db.flush()
        # await self.db.refresh(instance)

        return instance


    async def insert_batch(
        self,
        data_list: list,
        Model: Type[T]
    ) -> Sequence[T]:
        data_batch = [Model(**data) for data in data_list]

        self.db.add_all(data_batch)
        self.db.flush()

        return data_batch

    # =======================================
    # 2. Read Data
    # =======================================
    async def get_data_by_id(
        self,
        data_id: uuid.UUID,
        Model: Type[T]
    ) -> Optional[T]:
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
        Model: Type[T]
    ) -> Sequence[T]:
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
        Model: Type[T]
    ) -> Optional[T]:

        stmt = (
            update(Model)
            .where(Model.id == item_id)
            .values(**data)
            .returning(Model)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.scalar_one_or_none()


    async def update_data_with_refresh(
        self,
        data: dict,
        item_id: uuid.UUID,
        Model: Type[T]
    ) -> Optional[T]:
        model_data = self.db.get(Model, item_id)

        for key, value in data.items():
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
        Model: Type[T]
    ) -> uuid.UUID:
        
        stmt = (
            delete(Model)
            .where(Model.id == item_id)
            .returning(Model.id)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.scalar_one()
