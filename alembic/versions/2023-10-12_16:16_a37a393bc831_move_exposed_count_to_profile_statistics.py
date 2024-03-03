"""move exposed count to profile_statistics

Revision ID: a37a393bc831
Revises: 5014a1d75251
Create Date: 2023-10-12 16:16:04.210967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a37a393bc831"
down_revision = "5014a1d75251"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "profile_statistics",
        sa.Column(
            "confession_exposed_count",
            sa.Integer,
            nullable=False,
            default=0,
            server_default="0",
        ),
    )

    op.execute(
        "update profile_statistics set confession_exposed_count=p.confession_exposed_count from profile p where profile_discord_id=p.discord_id"
    )

    op.drop_column("profile", "confession_exposed_count")


def downgrade() -> None:
    op.add_column(
        "profile",
        sa.Column(
            "confession_exposed_count",
            sa.Integer,
            nullable=False,
            default=0,
            server_default="0",
        ),
    )

    op.execute(
        "update profile set confession_exposed_count=s.confession_exposed_count from profile_statistics s where discord_id=s.profile_discord_id"
    )

    op.drop_column("profile_statistics", "confession_exposed_count")
