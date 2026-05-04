"""Document model for uploaded PDF metadata and processing state."""

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import foreign

from app.database import db
from app.models.summary import Summary


class HistorialDocumento(db.Model):
    """Represents an uploaded document and its async processing lifecycle."""

    __tablename__ = "historial_documentos"
    ESTADOS_VALIDOS = ("pending", "processing", "completed", "failed")
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_historial_documentos_estado",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    extracto_texto = db.Column(db.Text, nullable=True)
    tamanio_bytes = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default=ESTADOS_VALIDOS[0])
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    usuario = db.relationship("User", backref=db.backref("documentos", lazy=True))
    resumenes = db.relationship(
        Summary,
        primaryjoin=lambda: HistorialDocumento.id == foreign(Summary.documento_id),
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self) -> dict:
        """Convert document instance to dictionary representation."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nombre_archivo": self.nombre_archivo,
            "extracto_texto": self.extracto_texto,
            "tamanio_bytes": self.tamanio_bytes,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
