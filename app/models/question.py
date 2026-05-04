"""Question model: historial de preguntas ligadas a documentos."""

from datetime import UTC, datetime

from sqlalchemy.orm import synonym

from app.database import db
from app.models.document import HistorialDocumento


class HistorialPregunta(db.Model):
    """Represents a question asked about a document."""

    __tablename__ = "historial_preguntas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    documento_id = db.Column(
        "document_id",
        db.Integer,
        db.ForeignKey("historial_documentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pregunta = db.Column(db.Text, nullable=False)
    respuesta = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # relationships for convenience
    usuario = db.relationship("User", backref=db.backref("preguntas", lazy=True))
    documento = db.relationship("HistorialDocumento", backref=db.backref("preguntas", lazy=True))

    # API-friendly aliases
    user_id = synonym("usuario_id")
    document_id = synonym("documento_id")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "documento_id": self.documento_id,
            "pregunta": self.pregunta,
            "respuesta": self.respuesta,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "document_id": self.document_id,
        }


Question = HistorialPregunta
