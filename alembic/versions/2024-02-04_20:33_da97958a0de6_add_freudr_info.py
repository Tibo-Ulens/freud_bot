"""add freudr info

Revision ID: da97958a0de6
Revises: a37a393bc831
Create Date: 2024-02-04 20:33:57.517848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "da97958a0de6"
down_revision = "a37a393bc831"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "profile",
        sa.Column(
            "crushes", sa.ARRAY(sa.BigInteger), nullable=False, server_default="{}"
        ),
    )


def downgrade() -> None:
    op.drop_column("profile", "crushes")
