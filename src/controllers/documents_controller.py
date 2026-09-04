import uuid

from src.services.database_service import DatabaseService
from src.models.documents import Document
from src.schemas.document_schemas import DocumentUpload


class DocumentsController(DatabaseService):

    def __init__(self, db_session):
        super().__init__(db_session)


    async def get_all_documents(self, skip: int, limit: int):
        doc_data = await self.fetch_all_data_all_data(Document, skip, limit)

        return {
            "success": True,
            "Message": f"{len(doc_data)} documents fetched successfully",
            "data": doc_data
        }

    async def get_document_by_id(self, id: uuid.UUID):
        doc_data = await self.fetch_data_by_id(Document, id)

        return {
            "success": True,
            "Message": "Document fetched successfully",
            "data": doc_data
        }


    async def upload_document(self, upload_data: DocumentUpload):

        cleaned_data = upload_data.model_dump(exclude_unset=True)

        doc_data = await self.insert_data(Document, cleaned_data)

        await self.save()

        return {
            "success": True,
            "Message": "Document inserted successfully",
            "data": doc_data
        }