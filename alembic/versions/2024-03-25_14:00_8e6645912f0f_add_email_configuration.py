"""add email configuration

Revision ID: 8e6645912f0f
Revises: f62b8b1e6c4f
Create Date: 2024-03-25 14:00:27.136121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8e6645912f0f"
down_revision = "f62b8b1e6c4f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "config", sa.Column("verification_email_smtp_user", sa.Text, nullable=True)
    )

    op.add_column(
        "config", sa.Column("verification_email_smtp_password", sa.Text, nullable=True)
    )

    op.add_column(
        "config",
        sa.Column(
            "verification_email_subject",
            sa.Text,
            nullable=False,
            default="",
            server_default="",
        ),
    )

    op.add_column(
        "config",
        sa.Column(
            "verification_email_body",
            sa.Text,
            nullable=False,
            default="",
            server_default="",
        ),
    )


def downgrade() -> None:
    op.drop_column("config", "verification_email_smtp_user")
    op.drop_column("config", "verification_email_smtp_password")
    op.drop_column("config", "verification_email_subject")
    op.drop_column("config", "verification_email_body")
