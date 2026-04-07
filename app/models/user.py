"""User model"""

from datetime import datetime, UTC
from app.database import db


class User(db.Model):
    """User entity representing registered users in the system"""

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    def to_dict(self):
        """Convert user instance to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
