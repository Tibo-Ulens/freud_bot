"""add confession exposure counter

Revision ID: 7f5cc27e7f61
Revises: 2adbec7716ff
Create Date: 2023-10-07 21:43:38.674746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f5cc27e7f61"
down_revision = "2adbec7716ff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "profile",
        sa.Column(
            "confession_exposed_count", sa.Integer, nullable=False, server_default="0"
        ),
    )


def downgrade() -> None:
    op.drop_column("profile", "confession_exposed_count")
