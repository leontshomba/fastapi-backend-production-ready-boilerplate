import asyncio

from src.config.database import AsyncSessionLocal
from src.services.database import insert_data

from src.models.documents import Document

data = {
    "name": "Common-prod-bugs",
    "description": "This document list common cloud environment productions bugs & how to fix them",
    "category": "cloud",
    "size": 14
}

async def main ():
    new_data = Document(
        name=data["name"],
        description=data["description"],
        category=data["category"],
        size=data["size"]
    )    

    print("Inserting...")

    async with AsyncSessionLocal() as db:
        result = await insert_data(db=db, model=new_data)

    print("Inserted data ID: ", result.id)
    print("Data: ", result.to_dict())

if __name__ == "__main__":
    asyncio.run(main())

