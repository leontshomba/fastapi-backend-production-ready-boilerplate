import asyncio

from src.config.database import AsyncSessionLocal
from src.services.database import insert_data, insert_batch

from src.models.documents import Document
from data.docs import sample_documents

data = {
    "name": "Common-prod-bugs",
    "description": "This document list common cloud environment productions bugs & how to fix them",
    "category": "cloud",
    "size": 14
}

async def main ():
    # new_data = Document(**data)    

    print("Inserting...")

    async with AsyncSessionLocal() as db:
        result = await insert_batch(db, sample_documents, Document)

    print(f"Successfully inserted {len(result)} documents!")

if __name__ == "__main__":
    asyncio.run(main())

