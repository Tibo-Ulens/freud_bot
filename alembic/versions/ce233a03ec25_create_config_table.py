"""create_config_table

Revision ID: ce233a03ec25
Revises: 6f04bc4e4691
Create Date: 2022-12-22 04:10:27.310547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ce233a03ec25"
down_revision = "6f04bc4e4691"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "config",
        sa.Column("guild_id", sa.Text, primary_key=True),
        sa.Column("verified_role", sa.Text, nullable=True),
        sa.UniqueConstraint("guild_id", name="unique_guild_id"),
        sa.UniqueConstraint("verified_role", name="unique_verified_role"),
    )


def downgrade() -> None:
    op.drop_table("config")
