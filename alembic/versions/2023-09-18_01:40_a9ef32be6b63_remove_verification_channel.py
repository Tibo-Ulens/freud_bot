"""remove_verification_channel

Revision ID: a9ef32be6b63
Revises: 3ce80343b85a
Create Date: 2023-09-18 01:40:58.433790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a9ef32be6b63"
down_revision = "3ce80343b85a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("config", "verification_channel")


def downgrade() -> None:
    op.add_column(
        "config", sa.Column("verification_channel", sa.BigInteger, nullable=True)
    )
