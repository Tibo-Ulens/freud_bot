"""create profile table

Revision ID: 8b81404b70b3
Revises:
Create Date: 2022-09-03 00:22:01.995652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8b81404b70b3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profile",
        sa.Column("discord_id", sa.Text, primary_key=True),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("confirmation_code", sa.Text),
        sa.UniqueConstraint("email", name="unique_email"),
        sa.UniqueConstraint("confirmation_code", name="unique_confirmation_code"),
    )


def downgrade() -> None:
    op.drop_table("profile")
