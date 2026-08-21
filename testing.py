import asyncio

from src.config.database import AsyncSessionLocal
from src.services.database import get_all_data

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

    print("Processing...")

    async with AsyncSessionLocal() as db:
        res = await get_all_data(db, 0, 5, Document)

    if res:
        print(f"Successfully fetched {len(res)} documents!")
    else:
        print("Result is empty")

if __name__ == "__main__":
    asyncio.run(main())

