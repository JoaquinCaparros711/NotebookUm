"""Summary model for document summaries"""

from datetime import datetime
from app.database import db


class Summary(db.Model):
    """Represents a summary generated for a document"""

    __tablename__ = "resumenes"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=True, index=True)  # Owner of the document
    summary_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Convert summary to dictionary representation"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "summary_text": self.summary_text,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
