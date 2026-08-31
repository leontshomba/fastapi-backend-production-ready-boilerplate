import asyncio

from src.config.database import AsyncSessionLocal
from src.services.database_service import DatabaseService

from src.models.documents import Document
from data.docs import sample_documents

data = {
    "name": "k8s-optimization-tips",
    "description": "A comprehensive guide at optimizing prroduction k8s clusters in production.",
    "category": "devops",
    "size": 27
}

id = "19ac7246-44b4-4e8e-8dd1-87d28b99815f"

async def main ():
    # new_data = Document(**data)    

    print("Processing...")

    async with AsyncSessionLocal() as db:
        service = DatabaseService(db)
        res = await service.insert_data(Document, data)

    if res:
        print(f"Successfully deleted document with id: {res.to_dict()}")
    else:
        print("Result is empty")

if __name__ == "__main__":
    asyncio.run(main())

