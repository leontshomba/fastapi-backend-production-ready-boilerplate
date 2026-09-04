from fastapi import APIRouter, Depends, Body
from  sqlalchemy.ext.asyncio import AsyncSession

import uuid

from src.config.database import get_db
from src.controllers.documents_controller import DocumentsController
from src.schemas.document_schemas import DocumentUpload


router = APIRouter()

@router.get("/{id}")
async def get_document_by_id(
    id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db)
):
    controller = DocumentsController(db_session)

    return await controller.get_document_by_id(id)


@router.post("/")
async def get_document_by_id(
    upload_data: DocumentUpload = Body(...),
    db_session: AsyncSession = Depends(get_db)
):
    controller = DocumentsController(db_session)

    return await controller.upload_document(upload_data)