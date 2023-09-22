"""add verification log channel

Revision ID: 2adbec7716ff
Revises: a9ef32be6b63
Create Date: 2023-09-22 16:09:43.916181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2adbec7716ff"
down_revision = "a9ef32be6b63"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "config",
        sa.Column("verification_logging_channel", sa.BigInteger, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("config", "verification_logging_channel")
