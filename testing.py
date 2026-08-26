import asyncio

from src.config.database import AsyncSessionLocal
from src.services.database import delete_data

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
        res = await delete_data(db, id, Document)

    if res:
        print(f"Successfully deleted document with id: {res}")
    else:
        print("Result is empty")

if __name__ == "__main__":
    asyncio.run(main())

