import uuid

from src.services.database_service import DatabaseService
from src.models.documents import Document
from src.schemas.document_schemas import DocumentUpload, DocumentUpdate


class DocumentsController(DatabaseService):

    def __init__(self, db_session):

        # Initialize the db service parent class
        super().__init__(db_session)

        self.db_model = Document

    async def get_all_documents(self, skip: int, limit: int):
        doc_data = await self.fetch_all_data(self.db_model, skip, limit)

        await self.save()

        return {
            "success": True,
            "Message": f"{len(doc_data)} documents fetched successfully",
            "data": doc_data
        }


    async def get_document_by_id(self, id: uuid.UUID):
        doc_data = await self.fetch_data_by_id(self.db_model, id)

        await self.save()

        return {
            "success": True,
            "Message": "Document fetched successfully",
            "data": doc_data
        }


    async def upload_document(self, upload_data: DocumentUpload):

        cleaned_data = upload_data.model_dump(exclude_unset=True)

        doc_data = await self.insert_data(self.db_model, cleaned_data)

        await self.save()

        return {
            "success": True,
            "Message": "Document inserted successfully",
            "data": doc_data
        }


    async def update_document(self, update_data: DocumentUpdate, id: uuid.UUID):

        cleaned_data = update_data.model_dump(exclude_unset=True)

        updated_doc = await self.update_data(self.db_model, cleaned_data, id)

        await self.save()

        return {
            "success": True,
            "Message": "Document updated successfully",
            "data": updated_doc
        }

    async def delete_document(self, id: uuid.UUID):

        updated_doc = await self.delete_data(self.db_model, id)

        await self.save()

        return {
            "success": True,
            "Message": "Document deleted successfully",
            "data": updated_doc
        }