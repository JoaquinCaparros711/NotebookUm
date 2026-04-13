"""Routes for document upload and asynchronous processing."""

from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from app.database import db
from app.models.document import HistorialDocumento
from app.services.async_tasks import process_document_task
from app.services.validation import (
    create_rfc9457_error,
    validate_file_size,
    validate_pdf_content_type,
)

documents_bp = Blueprint("documents", __name__, url_prefix="/api/v1/documento")


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
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        file.save(tmp_file)
        temp_pdf_path = tmp_file.name

    document = HistorialDocumento(
        usuario_id=usuario_id,
        nombre_archivo=file.filename,
        tamanio_bytes=file.content_length or Path(temp_pdf_path).stat().st_size,
        estado="pending",
    )
    db.session.add(document)
    db.session.commit()

    task_result = process_document_task.delay(
        user_id=usuario_id,
        document_id=document.id,
        pdf_path=temp_pdf_path,
    )

    response = {
        "document_id": document.id,
        "status": "pending",
        "job_id": task_result.id,
        "status_url": f"/api/v1/documento/{document.id}/status",
    }
    return jsonify(response), 202
