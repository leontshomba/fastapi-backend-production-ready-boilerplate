import uuid

from src.services.database_service import DatabaseService
from src.models.documents import Document


class DocumentsController(DatabaseService):

    def __init__(self, db_session):
        super().__init__(db_session)

    def get_document_by_id(self, id: uuid.UUID):
        return self.get_data_by_id(Document, id)