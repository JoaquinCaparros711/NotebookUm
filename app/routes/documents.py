"""Routes for document upload and asynchronous processing."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from celery.exceptions import CeleryError
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models.document import HistorialDocumento
from app.services.async_tasks import process_document_task
from app.services.document_service import (
    DocumentForbiddenError,
    DocumentNotFoundError,
    DocumentService,
    DocumentServiceError,
    DocumentValidationError,
)
from app.services.validation import (
    create_rfc9457_error,
    validate_file_size,
    validate_pdf_content_type,
)
from app.utils.errors import forbidden, internal_server_error, not_found

documents_bp = Blueprint("documents", __name__, url_prefix="/api/v1/documento")
documents_list_bp = Blueprint("documents_list", __name__, url_prefix="/api/v1/documentos")


@documents_bp.route("/upload", methods=["POST"])
def upload_document():
    """Upload a PDF document and enqueue asynchronous processing."""
    file = request.files.get("file")
    if file is None or not file.filename:
        return create_rfc9457_error(
            detail="A PDF file is required in form field 'file'.",
            instance="/api/v1/documento/upload",
        )

    try:
        validate_pdf_content_type(file)
        validate_file_size(file, max_size=current_app.config["MAX_UPLOAD_SIZE"])
    except ValueError as exc:
        return create_rfc9457_error(
            detail=str(exc),
            instance="/api/v1/documento/upload",
        )

    user_id = request.headers.get("X-User-ID", "1")
    try:
        usuario_id = int(user_id)
    except ValueError:
        return create_rfc9457_error(
            detail="Invalid X-User-ID header value.",
            instance="/api/v1/documento/upload",
        )

    file.stream.seek(0)
    suffix = Path(file.filename).suffix or ".pdf"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            file.save(tmp_file)
            temp_pdf_path = tmp_file.name
    except OSError:
        return internal_server_error(
            detail="Unable to store uploaded file for processing.",
            instance="/api/v1/documento/upload",
        )

    document = HistorialDocumento(
        usuario_id=usuario_id,
        nombre_archivo=file.filename,
        tamanio_bytes=file.content_length or Path(temp_pdf_path).stat().st_size,
        estado="pending",
    )
    try:
        db.session.add(document)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        _safe_delete(temp_pdf_path)
        return internal_server_error(
            detail="Unable to persist document metadata.",
            instance="/api/v1/documento/upload",
        )

    try:
        task_result = process_document_task.delay(
            user_id=usuario_id,
            document_id=document.id,
            pdf_path=temp_pdf_path,
        )
    except (CeleryError, RuntimeError):
        document.estado = "failed"
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        _safe_delete(temp_pdf_path)
        return internal_server_error(
            detail="Unable to enqueue document processing task.",
            instance="/api/v1/documento/upload",
        )

    response = {
        "document_id": document.id,
        "status": "pending",
        "job_id": task_result.id,
        "status_url": f"/api/v1/documento/{document.id}/status",
    }
    return jsonify(response), 202


@documents_bp.route("/<int:document_id>/status", methods=["GET"])
def get_document_status(document_id: int):
    """Return current processing status for an uploaded document."""
    document = db.session.get(HistorialDocumento, document_id)
    if document is None:
        return not_found(
            detail=f"Document with ID {document_id} not found",
            instance=f"/api/v1/documento/{document_id}/status",
        )

    return (
        jsonify(
            {
                "document_id": document.id,
                "status": document.estado,
                "created_at": document.created_at.isoformat() if document.created_at else None,
            }
        ),
        200,
    )


@documents_bp.route("/<int:document_id>", methods=["PATCH"])
def patch_document(document_id: int):
    """PATCH /api/v1/documento/{id}: update metadata; requires ownership via ``X-User-ID``."""
    user_id = request.headers.get("X-User-ID", "1")
    try:
        usuario_id = int(user_id)
    except ValueError:
        return create_rfc9457_error(
            detail="Invalid X-User-ID header value.",
            instance=f"/api/v1/documento/{document_id}",
        )

    instance = f"/api/v1/documento/{document_id}"
    try:
        document = DocumentService.update_document(
            document_id, usuario_id, request.get_json(silent=True)
        )
    except DocumentNotFoundError as exc:
        return not_found(detail=str(exc), instance=instance)
    except DocumentForbiddenError as exc:
        return forbidden(detail=str(exc), instance=instance)
    except DocumentValidationError as exc:
        return create_rfc9457_error(detail=str(exc), instance=instance)
    except DocumentServiceError:
        return internal_server_error(
            detail="Unable to update document.",
            instance=instance,
        )

    return jsonify(document.to_dict()), 200


@documents_bp.route("/<int:document_id>", methods=["DELETE"])
def delete_document(document_id: int):
    """DELETE /api/v1/documento/{id}: remove document and linked summaries (owner only)."""
    user_id = request.headers.get("X-User-ID", "1")
    try:
        usuario_id = int(user_id)
    except ValueError:
        return create_rfc9457_error(
            detail="Invalid X-User-ID header value.",
            instance=f"/api/v1/documento/{document_id}",
        )

    instance = f"/api/v1/documento/{document_id}"
    try:
        DocumentService.delete_document(document_id, usuario_id)
    except DocumentNotFoundError as exc:
        return not_found(detail=str(exc), instance=instance)
    except DocumentForbiddenError as exc:
        return forbidden(detail=str(exc), instance=instance)
    except DocumentServiceError:
        return internal_server_error(
            detail="Unable to delete document.",
            instance=instance,
        )

    return "", 204


@documents_list_bp.route("", methods=["GET"])
@documents_list_bp.route("/", methods=["GET"])
def list_documents():
    """GET /api/v1/documentos: all documents for ``X-User-ID``, or paginated with ``page`` and ``per_page``."""
    user_id = request.headers.get("X-User-ID", "1")
    try:
        usuario_id = int(user_id)
    except ValueError:
        return create_rfc9457_error(
            detail="Invalid X-User-ID header value.",
            instance="/api/v1/documentos",
        )

    page_arg = request.args.get("page")
    per_page_arg = request.args.get("per_page")
    if page_arg is not None and per_page_arg is not None:
        try:
            page = int(page_arg)
            per_page = int(per_page_arg)
            if page < 1 or per_page < 1:
                raise ValueError
        except ValueError:
            return create_rfc9457_error(
                detail="Query params 'page' and 'per_page' must be positive integers.",
                instance="/api/v1/documentos",
            )

        try:
            result = DocumentService.list_user_documents(
                usuario_id, page=page, per_page=per_page
            )
        except DocumentValidationError as exc:
            return create_rfc9457_error(detail=str(exc), instance="/api/v1/documentos")

        meta = result["pagination"]
        assert meta is not None
        return (
            jsonify(
                {
                    "items": [d.to_dict() for d in result["items"]],
                    "page": meta["page"],
                    "per_page": meta["per_page"],
                    "total": meta["total"],
                    "pages": meta["pages"],
                    "has_next": meta["has_next"],
                }
            ),
            200,
        )

    result = DocumentService.list_user_documents(usuario_id)
    return jsonify([d.to_dict() for d in result["items"]]), 200


def _safe_delete(path: str) -> None:
    """Delete a temporary file if it exists."""
    if os.path.exists(path):
        os.remove(path)
