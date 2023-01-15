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
        sa.Column("guild_id", sa.BigInteger, primary_key=True),
        sa.Column("verified_role", sa.BigInteger, nullable=True),
        sa.Column("verification_channel", sa.BigInteger, nullable=True),
        sa.Column("admin_role", sa.BigInteger, nullable=True),
        sa.Column("logging_channel", sa.BigInteger, nullable=True),
        sa.Column("confession_approval_channel", sa.BigInteger, nullable=True),
        sa.Column("confession_channel", sa.BigInteger, nullable=True),
        sa.UniqueConstraint("guild_id", name="unique_guild_id"),
        sa.UniqueConstraint("verified_role", name="unique_verified_role"),
        sa.UniqueConstraint("verification_channel", name="unique_verification_channel"),
        sa.UniqueConstraint("admin_role", name="unique_admin_role"),
        sa.UniqueConstraint("logging_channel", name="unique_logging_channel"),
        sa.UniqueConstraint(
            "confession_approval_channel", name="unique_confession_approval_channel"
        ),
        sa.UniqueConstraint("confession_channel", name="unique_confession_channel"),
    )


def downgrade() -> None:
    op.drop_table("config")
