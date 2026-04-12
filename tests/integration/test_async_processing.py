"""Integration tests for asynchronous document processing."""

from pathlib import Path

import pytest

from app import create_app
from app.database import db
from app.models.document import HistorialDocumento
from app.services.async_tasks import process_document_task


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    flask_app = create_app("testing")
    flask_app.config["CELERY_TASK_ALWAYS_EAGER"] = True
    flask_app.config["CELERY_TASK_EAGER_PROPAGATES"] = False

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.mark.integration
class TestAsyncDocumentProcessing:
    """Integration tests for Celery async processing task."""

    def test_process_document_task_executes_with_celery(self, app, tmp_path: Path):
        """Celery task executes and returns completed processing payload."""
        with app.app_context():
            document = HistorialDocumento(
                usuario_id=1,
                nombre_archivo="sample.pdf",
                tamanio_bytes=1024,
                estado="pending",
            )
            db.session.add(document)
            db.session.commit()

            pdf_path = tmp_path / "sample.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF")

            task_result = process_document_task.delay(
                user_id=1,
                document_id=document.id,
                pdf_path=str(pdf_path),
            )

            assert task_result.successful()
            result_payload = task_result.get(timeout=5)
            assert result_payload["status"] == "completed"
            assert result_payload["document_id"] == document.id

    def test_process_document_task_updates_status_in_database(self, app):
        """Task updates document status to failed when processing errors happen."""
        with app.app_context():
            document = HistorialDocumento(
                usuario_id=1,
                nombre_archivo="missing.pdf",
                tamanio_bytes=1024,
                estado="pending",
            )
            db.session.add(document)
            db.session.commit()

            task_result = process_document_task.delay(
                user_id=1,
                document_id=document.id,
                pdf_path="C:\\tmp\\this-file-does-not-exist.pdf",
            )

            task_result.get(timeout=5)
            db.session.refresh(document)
            assert document.estado == "failed"

