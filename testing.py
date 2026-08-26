import asyncio

from src.config.database import AsyncSessionLocal
from src.services.database import direct_update

from src.models.documents import Document
from data.docs import sample_documents

data = {
    "name": "kubernetes-security",
    "description": "A comprehensive guide at securing production kubernetes clusters."
}

id = "111c889e-506a-4f9d-9b64-3a5dabe119b5"

async def main ():
    # new_data = Document(**data)    

    print("Processing...")

    async with AsyncSessionLocal() as db:
        res = await direct_update(db, data, id, Document)

    if res:
        print(f"Successfully updated document with name: {res.name}")
    else:
        print("Result is empty")

if __name__ == "__main__":
    asyncio.run(main())

