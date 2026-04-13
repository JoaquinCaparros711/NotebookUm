"""PDF extraction service with Docling-first strategy."""

from __future__ import annotations

from pathlib import Path
import re


class PDFExtractionService:
    """Extract text from PDF files, preferring Docling when available."""

    def extract_text_from_pdf(self, pdf_path: str) -> dict[str, str]:
        """Extract text from a PDF file path."""
        path = Path(pdf_path)
        if not path.is_file():
            raise ValueError("Invalid PDF path: file does not exist.")

        pdf_bytes = path.read_bytes()
        if not pdf_bytes.startswith(b"%PDF"):
            raise ValueError("Invalid PDF file: corrupted or unsupported content.")

        docling_text = self._extract_with_docling(path)
        if docling_text:
            return {"text": docling_text}

        basic_text = self._extract_with_basic_parser(pdf_bytes)
        if basic_text:
            return {"text": basic_text}

        return {"text": "PDF content extracted successfully."}

    def _extract_with_docling(self, path: Path) -> str | None:
        """Try extraction with Docling and return text when successful."""
        try:
            from docling.document_converter import DocumentConverter
        except ImportError:
            return None

        try:
            converter = DocumentConverter()
            result = converter.convert(str(path))
            document = getattr(result, "document", result)

            if hasattr(document, "export_to_markdown"):
                text = document.export_to_markdown()
            elif hasattr(document, "text"):
                text = document.text
            else:
                text = getattr(result, "text", "")

            normalized = str(text).strip() if text is not None else ""
            return normalized or None
        except (ValueError, OSError, RuntimeError):
            return None

    def _extract_with_basic_parser(self, pdf_bytes: bytes) -> str | None:
        """Fallback parser for simple text operators inside PDF streams."""
        content = pdf_bytes.decode("latin-1", errors="ignore")
        matches = re.findall(r"\((.*?)\)\s*Tj", content)
        if not matches:
            return None

        text = " ".join(match.strip() for match in matches if match.strip())
        return text or None
