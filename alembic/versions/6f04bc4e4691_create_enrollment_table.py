"""create enrollment table

Revision ID: 6f04bc4e4691
Revises: a2bd79234f94
Create Date: 2022-10-01 18:00:28.108732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6f04bc4e4691"
down_revision = "a2bd79234f94"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enrollment",
        sa.Column("profile_id", sa.Text, primary_key=True),
        sa.Column("course_id", sa.Text, primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("enrollment")
