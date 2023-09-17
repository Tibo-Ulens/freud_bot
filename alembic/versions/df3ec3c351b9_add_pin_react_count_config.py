"""add pin react count config

Revision ID: df3ec3c351b9
Revises: 30892f96f367
Create Date: 2023-09-11 19:33:05.617237

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "df3ec3c351b9"
down_revision = "30892f96f367"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "config",
        sa.Column(
            "pin_reaction_threshold", sa.Integer, nullable=False, server_default="3"
        ),
    )


def downgrade() -> None:
    op.drop_column("config", "pin_reaction_threshold")
