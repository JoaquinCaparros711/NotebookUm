"""Summary generation service with OpenAI integration and local fallbacks."""

from __future__ import annotations

import os
import time

from openai import OpenAI

from app.database import db
from app.models.document import HistorialDocumento
from app.models.summary import Summary


def initialize_openai_client(api_key: str | None = None) -> OpenAI | None:
    """Initialize and return an OpenAI client when an API key is available."""
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    if not resolved_api_key:
        return None
    return OpenAI(api_key=resolved_api_key)


class SummaryService:
    """Service layer for text summarization workflows and summary retrieval."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.client = initialize_openai_client(api_key)

    def get_summary_by_document_id(self, document_id: int) -> Summary | None:
        """
        Retrieve a summary record by document_id from the database.

        Args:
            document_id: The ID of the document to retrieve summary for

        Returns:
            Summary object if found, None otherwise
        """
        return Summary.query.filter_by(document_id=document_id).first()

    def check_user_ownership(self, summary: Summary, user_id: int) -> bool:
        """
        Check if a user owns a summary based on user_id.

        Args:
            summary: Summary object to check ownership for
            user_id: The user ID to check against

        Returns:
            True if user owns the summary or summary has no user restriction,
            False if user doesn't own the summary
        """
        if summary.user_id is None:
            return True
        return summary.user_id == user_id

    def check_document_ownership(self, document_id: int, user_id: int) -> bool:
        """
        Verify that *user_id* is the owner of the parent document (RF-018).

        Looks up ``HistorialDocumento`` by primary key and compares its
        ``usuario_id`` with the requesting ``user_id``.  When the document
        record does not exist the method grants access (no restriction can
        be enforced against a missing resource).

        Args:
            document_id: Primary key of the document to verify ownership for.
            user_id: ID of the user requesting access.

        Returns:
            True  – user owns the document, or the document was not found.
            False – another user owns the document.
        """
        document = db.session.get(HistorialDocumento, document_id)
        if document is None:
            return True
        return document.usuario_id == user_id

    @staticmethod
    def get_status_message(summary: Summary) -> str | None:
        """Return a human-readable state message for non-completed summaries.

        Completed summaries need no overlay message, so this method returns
        ``None`` in that case.  All other states produce a Spanish message
        intended to be included in the API response payload under the key
        ``"message"``, satisfying HU-3 escenario 3 (spec.md).

        Args:
            summary: The Summary instance whose state is being evaluated.

        Returns:
            ``None`` when ``summary.status == "completed"``.
            A non-empty string for every other known (or unknown) status.
        """
        _MESSAGES: dict[str, str] = {
            "pending": (
                "El resumen está en cola de procesamiento. "
                "Por favor, intente de nuevo en unos momentos."
            ),
            "processing": (
                "El resumen está siendo generado. "
                "Por favor, intente de nuevo en unos momentos."
            ),
            "failed": (
                "La generación del resumen falló. "
                "Por favor, vuelva a cargar el documento para reintentar."
            ),
        }
        if summary.status == "completed":
            return None
        return _MESSAGES.get(
            summary.status,
            f"El resumen no está disponible (estado: {summary.status}).",
        )

    @staticmethod
    def detect_language(text: str) -> str:

        """Detect basic language for Spanish/English support."""
        lowered = text.lower()
        spanish_markers = (" el ", " la ", " de ", " y ", " que ", " los ", " las ", " un ")
        return "es" if any(marker in f" {lowered} " for marker in spanish_markers) else "en"

    def summarize_text(
        self,
        text: str,
        language: str | None = None,
        max_chunk_chars: int = 12000,
        retries: int = 2,
    ) -> str:
        """Generate a summary for text, using hierarchical mode for long inputs."""
        normalized = (text or "").strip()
        if not normalized:
            raise ValueError("Cannot summarize empty text.")

        lang = language or self.detect_language(normalized)
        if len(normalized) > max_chunk_chars:
            return self.hierarchical_summarize(
                normalized,
                language=lang,
                max_chunk_chars=max_chunk_chars,
                retries=retries,
            )
        return self._summarize_with_retry(normalized, language=lang, retries=retries)

    def hierarchical_summarize(
        self,
        text: str,
        language: str,
        max_chunk_chars: int = 12000,
        retries: int = 2,
    ) -> str:
        """Summarize long text by chunking and recursively summarizing."""
        chunks = [text[i : i + max_chunk_chars] for i in range(0, len(text), max_chunk_chars)]
        partial_summaries = [
            self._summarize_with_retry(chunk, language=language, retries=retries)
            for chunk in chunks
        ]
        combined = "\n".join(partial_summaries)
        return self._summarize_with_retry(combined, language=language, retries=retries)

    def _summarize_with_retry(self, text: str, language: str, retries: int) -> str:
        """Run summary generation with bounded retries."""
        attempts = retries + 1
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                return self._summarize_once(text, language=language)
            except (RuntimeError, ValueError) as exc:
                last_error = exc
                if attempt == attempts - 1:
                    break
                time.sleep(min(0.2 * (attempt + 1), 1.0))

        if last_error:
            raise last_error
        raise RuntimeError("Summary generation failed unexpectedly.")

    def _summarize_once(self, text: str, language: str) -> str:
        """Generate one summary attempt using OpenAI when available, otherwise fallback."""
        if self.client is not None:
            result = self._summarize_with_openai(text, language=language)
            if result.strip():
                return result

        fallback = self._summarize_locally(text, language=language)
        if not fallback.strip():
            raise RuntimeError("Unable to generate summary.")
        return fallback

    def _summarize_with_openai(self, text: str, language: str) -> str:
        """Call OpenAI Responses API for summary generation."""
        language_name = "Spanish" if language == "es" else "English"
        try:
            completion = self.client.chat.completions.create(  # type: ignore[union-attr]
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a concise summarization assistant. "
                            f"Respond only in {language_name}."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the following text:\n\n{text}",
                    },
                ],
            )
            output_text = ""
            try:
                output_text = completion.choices[0].message.content or ""
            except Exception:
                output_text = ""
            return str(output_text).strip()
        except Exception:
            return ""

    @staticmethod
    def _summarize_locally(text: str, language: str) -> str:
        """Generate a deterministic local summary fallback."""
        normalized = " ".join(text.split())
        if not normalized:
            return ""

        parts = [
            segment.strip()
            for segment in normalized.replace("?", ".").split(".")
            if segment.strip()
        ]
        if not parts:
            parts = [normalized]

        selected = parts[:2]
        body = ". ".join(selected)
        if not body.endswith("."):
            body += "."

        prefix = "Resumen: " if language == "es" else "Summary: "
        return f"{prefix}{body}"
