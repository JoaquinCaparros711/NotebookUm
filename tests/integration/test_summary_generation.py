"""Integration tests for summary generation service."""

import pytest

from app.services.summary_service import SummaryService


@pytest.mark.integration
class TestSummaryGenerationService:
    """Integration tests for OpenAI-backed summary generation."""

    def test_generate_summary_from_text(self):
        """OpenAI summary generation returns a non-empty summary for valid text."""
        service = SummaryService()
        source_text = (
            "Software architecture defines system structure and tradeoffs. "
            "A good design balances maintainability, performance, and reliability."
        )

        result = service.summarize_text(source_text, language="en")

        assert isinstance(result, str)
        assert result.strip() != ""

    def test_generate_hierarchical_summary_for_long_text(self):
        """Long documents are summarized successfully using hierarchical strategy."""
        service = SummaryService()
        long_text = " ".join(["This paragraph explains architecture decisions."] * 12000)

        result = service.summarize_text(long_text, language="en")

        assert isinstance(result, str)
        assert result.strip() != ""

    def test_generate_summary_supports_spanish_and_english(self):
        """Service generates summaries for both Spanish and English documents."""
        service = SummaryService()
        text_es = (
            "La arquitectura de software debe priorizar mantenibilidad, "
            "escalabilidad y confiabilidad para evolucionar con el negocio."
        )
        text_en = (
            "Software architecture should prioritize maintainability, "
            "scalability, and reliability to evolve with business needs."
        )

        summary_es = service.summarize_text(text_es, language="es")
        summary_en = service.summarize_text(text_en, language="en")

        assert isinstance(summary_es, str)
        assert summary_es.strip() != ""
        assert isinstance(summary_en, str)
        assert summary_en.strip() != ""

