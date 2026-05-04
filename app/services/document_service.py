"""Business logic for historial de documentos (list, update, delete)."""

from __future__ import annotations

from typing import Any, List, Optional, TypedDict

from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models.document import HistorialDocumento
from app.models.summary import Summary


class DocumentServiceError(Exception):
    """Base error for document service operations."""

    pass


class DocumentNotFoundError(DocumentServiceError):
    """Raised when a document id does not exist."""

    pass


class DocumentForbiddenError(DocumentServiceError):
    """Raised when the authenticated user does not own the document."""

    pass


class DocumentValidationError(DocumentServiceError):
    """Raised when PATCH payload or list pagination parameters are invalid."""

    pass


class _PaginationMeta(TypedDict):
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool


class ListDocumentsResult(TypedDict):
    items: List[HistorialDocumento]
    pagination: Optional[_PaginationMeta]


class DocumentService:
    """Service for listing, updating, and deleting user-owned documents."""

    @staticmethod
    def list_user_documents(
        usuario_id: int,
        *,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> ListDocumentsResult:
        """Return documents for ``usuario_id``, optionally paginated.

        If both ``page`` and ``per_page`` are set, returns a page of results with
        ``pagination`` metadata. If neither is set, returns all documents (newest
        first).
        """
        if page is not None and per_page is not None:
            if page < 1 or per_page < 1:
                raise DocumentValidationError(
                    "Query params 'page' and 'per_page' must be positive integers."
                )
            query = (
                HistorialDocumento.query.filter_by(usuario_id=usuario_id)
                .order_by(HistorialDocumento.id.desc())
            )
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": list(pagination.items),
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                },
            }

        query = (
            HistorialDocumento.query.filter_by(usuario_id=usuario_id)
            .order_by(HistorialDocumento.id.desc())
        )
        return {"items": query.all(), "pagination": None}

    @staticmethod
    def update_document(document_id: int, usuario_id: int, data: Any) -> HistorialDocumento:
        """Apply metadata updates; raises if not found, forbidden, or invalid body."""
        document = db.session.get(HistorialDocumento, document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} not found")

        if document.usuario_id != usuario_id:
            raise DocumentForbiddenError("You are not allowed to modify this document.")

        if not isinstance(data, dict):
            raise DocumentValidationError("Request body must be a JSON object.")

        updated = False
        if "nombre_archivo" in data:
            name = data["nombre_archivo"]
            if not isinstance(name, str) or not name.strip():
                raise DocumentValidationError(
                    "Field 'nombre_archivo' must be a non-empty string."
                )
            document.nombre_archivo = name.strip()
            updated = True

        if not updated:
            raise DocumentValidationError(
                "No supported metadata fields to update. Supported: nombre_archivo."
            )

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise DocumentServiceError("Unable to update document.") from None

        return document

    @staticmethod
    def delete_document(document_id: int, usuario_id: int) -> None:
        """Delete document and linked summaries; raises if not found or forbidden."""
        document = db.session.get(HistorialDocumento, document_id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {document_id} not found")

        if document.usuario_id != usuario_id:
            raise DocumentForbiddenError("You are not allowed to delete this document.")

        try:
            # Rely on database-level ON DELETE CASCADE and SQLAlchemy relationship
            # cascade settings to remove dependent summaries when the document
            # is deleted. This avoids manual delete queries which may bypass
            # relationship bookkeeping.
            db.session.delete(document)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise DocumentServiceError("Unable to delete document.") from None
