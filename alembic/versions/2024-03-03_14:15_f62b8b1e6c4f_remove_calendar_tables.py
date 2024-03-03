"""remove calendar tables

Revision ID: f62b8b1e6c4f
Revises: da97958a0de6
Create Date: 2024-03-03 14:15:49.368952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f62b8b1e6c4f"
down_revision = "da97958a0de6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("enrollment")
    op.drop_table("lecture")
    op.drop_table("course")


def downgrade() -> None:
    op.create_table(
        "course",
        sa.Column("code", sa.Text, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.UniqueConstraint("code", name="unique_code"),
        sa.UniqueConstraint("name", name="unique_name"),
    )

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

    op.create_table(
        "enrollment",
        sa.Column("profile_discord_id", sa.Text, primary_key=True),
        sa.Column("course_code", sa.Text, primary_key=True),
    )
