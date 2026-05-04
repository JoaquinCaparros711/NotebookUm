"""Summary model for document summaries."""

from datetime import UTC, datetime

from sqlalchemy.orm import synonym
from sqlalchemy import ForeignKey

from app.database import db


class Resumen(db.Model):
    """Represents a generated summary linked to a processed document."""

    __tablename__ = "resumenes"

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(
        "document_id",
        db.Integer,
        ForeignKey("historial_documentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contenido = db.Column("summary_text", db.Text, nullable=False)
    modelo_utilizado = db.Column(db.String(100), nullable=False, default="gpt-4o")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    # Legacy compatibility fields used by already-implemented routes/tests.
    user_id = db.Column(db.Integer, nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Backward-compatible attribute aliases.
    document_id = synonym("documento_id")
    summary_text = synonym("contenido")

    def to_dict(self) -> dict:
        """Convert summary to dictionary representation."""
        return {
            "id": self.id,
            "documento_id": self.documento_id,
            "contenido": self.contenido,
            "modelo_utilizado": self.modelo_utilizado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "document_id": self.document_id,
            "summary_text": self.summary_text,
            "status": self.status,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


Summary = Resumen
