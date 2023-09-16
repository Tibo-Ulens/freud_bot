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
    # guild_name
    op.add_column(
        "config",
        sa.Column(
            "verify_email_message",
            sa.Text,
            nullable=False,
            server_default="Click the button to verify your email to gain access to {guild_name}",
        ),
    )
    # old
    # new
    op.add_column(
        "config",
        sa.Column(
            "new_email_message",
            sa.Text,
            nullable=False,
            server_default="Your email has been updated from '{old}' to '{new}' and a new code has been sent to '{new}'",
        ),
    )
    # email
    op.add_column(
        "config",
        sa.Column(
            "invalid_email_message",
            sa.Text,
            nullable=False,
            server_default="'{email}' does not look like a valid email, please try again",
        ),
    )
    # email
    op.add_column(
        "config",
        sa.Column(
            "duplicate_email_message",
            sa.Text,
            nullable=False,
            server_default="'{email}' is already in use",
        ),
    )

    # email
    op.add_column(
        "config",
        sa.Column(
            "verify_code_message",
            sa.Text,
            nullable=False,
            server_default="A verification code was sent to {email}, click the button below to submit it",
        ),
    )
    # code
    op.add_column(
        "config",
        sa.Column(
            "invalid_code_message",
            sa.Text,
            nullable=False,
            server_default="'{code}' is not a valid code",
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

    # guild_name
    op.add_column(
        "config",
        sa.Column(
            "welcome_message",
            sa.Text,
            nullable=False,
            server_default="Welcome to {guild_name}",
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
