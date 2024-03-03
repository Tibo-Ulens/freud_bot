"""create course table

Revision ID: a2bd79234f94
Revises: 8b81404b70b3
Create Date: 2022-09-28 17:37:16.370716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a2bd79234f94"
down_revision = "8b81404b70b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course",
        sa.Column("code", sa.Text, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.UniqueConstraint("code", name="unique_code"),
        sa.UniqueConstraint("name", name="unique_name"),
    )


def downgrade() -> None:
    op.drop_table("course")
