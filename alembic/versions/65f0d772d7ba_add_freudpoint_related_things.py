"""add FreudPoint related things

Revision ID: 65f0d772d7ba
Revises: 2adbec7716ff
Create Date: 2023-10-05 16:26:53.915342

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "65f0d772d7ba"
down_revision = "2adbec7716ff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profile_statistics",
        sa.Column(
            "profile_discord_id",
            sa.BigInteger,
            sa.ForeignKey("profile.discord_id"),
            nullable=False,
        ),
        sa.Column(
            "config_guild_id",
            sa.BigInteger,
            sa.ForeignKey("config.guild_id"),
            nullable=False,
        ),
        sa.Column(
            "freudpoints", sa.Integer, nullable=False, default=0, server_default="0"
        ),
        sa.Column(
            "spendable_freudpoints",
            sa.Integer,
            nullable=False,
            default=1,
            server_default="1",
        ),
    )

    op.create_primary_key(
        "pk_profilestat_discordid_guildid",
        "profile_statistics",
        ["profile_discord_id", "config_guild_id"],
    )

    op.create_check_constraint(
        "freudpoints_min_0", "profile_statistics", "freudpoints >= 0"
    )
    op.create_check_constraint(
        "spendable_freudpoints_min_0",
        "profile_statistics",
        "spendable_freudpoints >= 0",
    )

    op.add_column(
        "config",
        sa.Column(
            "max_spendable_freudpoints",
            sa.Integer,
            nullable=False,
            default=5,
            server_default="5",
        ),
    )

    op.create_check_constraint(
        "max_spendable_freudpoints_min_0", "config", "max_spendable_freudpoints >= 0"
    )


def downgrade() -> None:
    op.drop_constraint("max_spendable_freudpoints_min_0", "config", type_="check")

    op.drop_column("config", "max_spendable_freudpoints")

    op.drop_constraint(
        "spendable_freudpoints_min_0", "profile_statistics", type_="check"
    )
    op.drop_constraint("freudpoints_min_0", "profile_statistics", type_="check")

    op.drop_table("profile_statistics")
