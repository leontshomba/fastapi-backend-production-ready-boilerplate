from typing import TypeVar, Type, Sequence, Optional
import uuid

from sqlalchemy import insert, select, update, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

T = TypeVar("T", bound=Base)

class DatabaseService():

    def __init__(self, db_session: AsyncSession):
        self.db: AsyncSession = db_session


    async def save(self):
        """Commits the current transaction. Used as the final 'seal' in the Controller."""
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            print(f"Database commit failed: {e}")
            raise


    # =======================================
    # 1. Create Data
    # =======================================
    async def add_data(
        self,
        Model: Type[T],
        data: dict,
    ) -> T:
        #This function relies on the ORM Unit of Work pattern for data insertion
        instance = Model(**data)

        self.db.add(instance)
        await self.db.flush()

        return instance


    async def insert_data(
        self,
        Model: Type[T],
        data: dict,
    ) -> T:
        #This function does direct insertion
        stmt = insert(Model).values(**data).returning(Model)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()


    async def insert_batch(
        self,
        Model: Type[T],
        data_list: list[dict],
        # For idempotent insertion
        unique_column_name: str
    ) -> int:

        payloads = [item for item in data_list]

        target_constraint_column = getattr(Model, unique_column_name)

        stmt = (
            pg_insert(Model)
            .values(payloads)
            .on_conflict_do_nothing(
                index_elements=[target_constraint_column]
            )
            .returning(target_constraint_column)
        )

        result = await self.db.execute(stmt)

        return len(result.scalars().all())

    # =======================================
    # 2. Read Data
    # =======================================
    async def get_data_by_id(
        self,
        Model: Type[T],
        data_id: uuid.UUID
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

        return result.scalar_one_or_none()


    async def update_orm(
        self,
        data: dict,
        item_id: uuid.UUID,
        Model: Type[T]
    ) -> Optional[T]:
        """ORM-based update. Best when you need to verify existing state before changing."""

        model_data = await self.db.get(Model, item_id)
        if not model_data:
            return None

        for key, value in data.items():
            if hasattr(model_data, key):
                setattr(model_data, key, value)

        await self.db.flush()
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

        return result.scalar_one_or_none()
