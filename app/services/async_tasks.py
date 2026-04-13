"""Celery task configuration and async document processing workflow."""

from __future__ import annotations

import os

from celery import Celery
from flask import has_app_context

from app import create_app
from app.database import db
from app.models.document import HistorialDocumento
from app.models.summary import Summary
from app.services.pdf_service import PDFExtractionService
from app.services.summary_service import SummaryService


celery_app = Celery(
    "notebookum",
    broker=os.getenv("CELERY_BROKER_URL", "memory://"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "cache+memory://"),
)
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=False,
)


@celery_app.task(name="process_document_task")
def process_document_task(user_id: int, document_id: int, pdf_path: str) -> dict:
    """Process an uploaded PDF asynchronously and persist summary data."""
    if has_app_context():
        return _process_document_task_impl(user_id=user_id, document_id=document_id, pdf_path=pdf_path)

    flask_app = create_app(os.getenv("FLASK_ENV", "testing"))
    with flask_app.app_context():
        return _process_document_task_impl(user_id=user_id, document_id=document_id, pdf_path=pdf_path)


def _process_document_task_impl(user_id: int, document_id: int, pdf_path: str) -> dict:
    """Internal document processing implementation."""
    document = db.session.get(HistorialDocumento, document_id)
    if document is None:
        return {"status": "failed", "document_id": document_id, "error": "Document not found"}

    try:
        document.estado = "processing"
        db.session.commit()

        extraction_service = PDFExtractionService()
        extraction_result = extraction_service.extract_text_from_pdf(pdf_path)
        extracted_text = extraction_result.get("text", "").strip()
        document.extracto_texto = extracted_text

        summary_service = SummaryService()
        summary_text = summary_service.summarize_text(
            extracted_text,
            language=summary_service.detect_language(extracted_text),
        )

        summary = Summary(
            document_id=document.id,
            summary_text=summary_text,
            user_id=user_id,
            status="completed",
        )
        db.session.add(summary)

        document.estado = "completed"
        db.session.commit()
        return {
            "status": "completed",
            "document_id": document.id,
            "summary_id": summary.id,
        }
    except Exception as exc:
        document.estado = "failed"
        db.session.commit()
        return {"status": "failed", "document_id": document_id, "error": str(exc)}
