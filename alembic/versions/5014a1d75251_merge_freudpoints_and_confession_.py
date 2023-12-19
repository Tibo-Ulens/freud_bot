"""merge freudpoints and confession exposure

Revision ID: 5014a1d75251
Revises: 65f0d772d7ba, 7f5cc27e7f61
Create Date: 2023-10-12 16:13:29.299389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5014a1d75251"
down_revision = ("65f0d772d7ba", "7f5cc27e7f61")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
