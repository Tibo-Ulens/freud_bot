"""create_lecture_table

Revision ID: 30892f96f367
Revises: ce233a03ec25
Create Date: 2022-12-25 21:12:22.880769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "30892f96f367"
down_revision = "ce233a03ec25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lecture",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("course_code", sa.Text, nullable=False),
        sa.Column("course_name", sa.Text, nullable=False),
        sa.Column("start_date", sa.Text, nullable=False),
        sa.Column("start_time", sa.Text, nullable=False),
        sa.Column("end_date", sa.Text, nullable=False),
        sa.Column("end_time", sa.Text, nullable=False),
        sa.Column("lecture_type", sa.Text, nullable=False),
        sa.Column("lecturer", sa.Text, nullable=False),
        sa.Column("classroom", sa.Text, nullable=False),
        sa.Column("building", sa.Text, nullable=False),
        sa.Column("campus", sa.Text, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("lecture")
