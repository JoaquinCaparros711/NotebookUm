"""Create historial_preguntas table for question history.

Revision ID: 8c5d9e2f1a4b
Revises: f2a1d9b3c4e7
Create Date: 2026-05-05 00:01:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c5d9e2f1a4b"
down_revision: Union[str, None] = "f2a1d9b3c4e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create historial_preguntas table with relationships to usuarios and historial_documentos."""
    op.create_table(
        "historial_preguntas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("pregunta", sa.Text(), nullable=False),
        sa.Column("respuesta", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["historial_documentos.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes on foreign keys for performance
    op.create_index(
        op.f("ix_historial_preguntas_usuario_id"),
        "historial_preguntas",
        ["usuario_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_historial_preguntas_document_id"),
        "historial_preguntas",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop historial_preguntas table and indexes."""
    op.drop_index(
        op.f("ix_historial_preguntas_document_id"),
        table_name="historial_preguntas",
    )
    op.drop_index(
        op.f("ix_historial_preguntas_usuario_id"),
        table_name="historial_preguntas",
    )
    op.drop_table("historial_preguntas")
