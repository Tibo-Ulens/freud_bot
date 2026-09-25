"""add email blacklist

Revision ID: cab813bc6e49
Revises: b7e2d5656c86
Create Date: 2026-09-25 21:00:41.513466

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cab813bc6e49"
down_revision = "b7e2d5656c86"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_blacklist",
        sa.Column(
            "guild_id",
            sa.BigInteger,
            sa.ForeignKey("config.guild_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("email", sa.Text, primary_key=True),
        # Set when the entry was created by banning this account, so unbanning
        # it can lift the entry again
        sa.Column("banned_discord_id", sa.BigInteger, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # email
    op.add_column(
        "config",
        sa.Column(
            "blacklisted_email_message",
            sa.Text,
            nullable=False,
            server_default="'{email}' is not allowed to verify in this server, please contact a server admin if you think this is a mistake",
        ),
    )


def downgrade() -> None:
    op.drop_column("config", "blacklisted_email_message")
    op.drop_table("email_blacklist")
