"""add verification messages config

Revision ID: 3ce80343b85a
Revises: df3ec3c351b9
Create Date: 2023-09-15 23:55:58.453911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3ce80343b85a"
down_revision = "df3ec3c351b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "config",
        sa.Column(
            "verify_email_message",
            sa.Text,
            nullable=False,
            server_default="Click the button to verify your email",
        ),
    )
    op.add_column(
        "config",
        sa.Column(
            "new_email_message",
            sa.Text,
            nullable=False,
            server_default="A new code has been sent",
        ),
    )
    op.add_column(
        "config",
        sa.Column(
            "invalid_email_message",
            sa.Text,
            nullable=False,
            server_default="This does not look like a valid email, please try again",
        ),
    )
    op.add_column(
        "config",
        sa.Column(
            "duplicate_email_message",
            sa.Text,
            nullable=False,
            server_default="Duplicate email",
        ),
    )

    op.add_column(
        "config",
        sa.Column(
            "verify_code_message",
            sa.Text,
            nullable=False,
            server_default="Click the button to verify your code",
        ),
    )
    op.add_column(
        "config",
        sa.Column(
            "invalid_code_message",
            sa.Text,
            nullable=False,
            server_default="Invalid code",
        ),
    )

    op.add_column(
        "config",
        sa.Column(
            "already_verified_message",
            sa.Text,
            nullable=False,
            server_default="You are already verified",
        ),
    )

    op.add_column(
        "config",
        sa.Column(
            "welcome_message",
            sa.Text,
            nullable=False,
            server_default="Welcome to {name}",
        ),
    )


def downgrade() -> None:
    op.drop_column("config", "verify_email_message")
    op.drop_column("config", "new_email_message")
    op.drop_column("config", "invalid_email_message")
    op.drop_column("config", "duplicate_email_message")
    op.drop_column("config", "verify_code_message")
    op.drop_column("config", "invalid_code_message")
    op.drop_column("config", "already_verified_message")
    op.drop_column("config", "welcome_message")
