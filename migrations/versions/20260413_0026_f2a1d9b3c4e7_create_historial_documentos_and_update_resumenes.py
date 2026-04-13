"""Create historial_documentos table and update resumenes schema.

Revision ID: f2a1d9b3c4e7
Revises: ab534f6e478d
Create Date: 2026-04-13 00:26:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a1d9b3c4e7"
down_revision: Union[str, None] = "ab534f6e478d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "historial_documentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("nombre_archivo", sa.String(length=255), nullable=False),
        sa.Column("extracto_texto", sa.Text(), nullable=True),
        sa.Column("tamanio_bytes", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_historial_documentos_usuario_id"),
        "historial_documentos",
        ["usuario_id"],
        unique=False,
    )

    with op.batch_alter_table("resumenes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("modelo_utilizado", sa.String(length=100), nullable=False, server_default="gpt-4o")
        )
        batch_op.create_foreign_key(
            "fk_resumenes_document_id_historial_documentos",
            "historial_documentos",
            ["document_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("resumenes", schema=None) as batch_op:
        batch_op.drop_constraint("fk_resumenes_document_id_historial_documentos", type_="foreignkey")
        batch_op.drop_column("modelo_utilizado")

    op.drop_index(op.f("ix_historial_documentos_usuario_id"), table_name="historial_documentos")
    op.drop_table("historial_documentos")
