"""Integration tests for PDF extraction with Docling."""

from pathlib import Path

import pytest

from app.services.pdf_service import PDFExtractionService


@pytest.mark.integration
class TestPDFExtractionService:
    """Integration tests for PDFExtractionService."""

    def test_extract_text_from_sample_pdf(self, tmp_path: Path):
        """Docling extracts text from a valid sample PDF."""
        pdf_path = tmp_path / "sample.pdf"
        pdf_path.write_bytes(
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] >>\nendobj\n"
            b"trailer\n<< /Root 1 0 R >>\n%%EOF"
        )

        service = PDFExtractionService()
        result = service.extract_text_from_pdf(str(pdf_path))

        assert isinstance(result, dict)
        assert "text" in result
        assert isinstance(result["text"], str)
        assert result["text"].strip() != ""

    def test_extract_text_from_corrupted_pdf_raises_value_error(self, tmp_path: Path):
        """Corrupted PDF handling raises ValueError with clear message."""
        corrupted_pdf_path = tmp_path / "corrupted.pdf"
        corrupted_pdf_path.write_bytes(b"not-a-valid-pdf-content")

        service = PDFExtractionService()

        with pytest.raises(ValueError) as exc_info:
            service.extract_text_from_pdf(str(corrupted_pdf_path))

        assert "corrupted" in str(exc_info.value).lower() or "invalid pdf" in str(
            exc_info.value
        ).lower()

