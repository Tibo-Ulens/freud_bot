"""normalize profile email subaddressing

Revision ID: b7e2d5656c86
Revises: 8e6645912f0f
Create Date: 2026-09-25 20:35:26.725090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7e2d5656c86"
down_revision = "8e6645912f0f"
branch_labels = None
depends_on = None


# local+tag@domain -> local@domain
NORMALIZED_EMAIL = r"regexp_replace(email, '\+[^@]*@', '@')"


def upgrade() -> None:
    # Profiles that only differ in their subaddress belong to the same mailbox,
    # refuse to pick one automatically and let an admin resolve them instead
    collisions = (
        op.get_bind()
        .execute(
            sa.text(
                f"""
                SELECT {NORMALIZED_EMAIL} AS normalized, array_agg(discord_id ORDER BY discord_id)
                FROM profile
                GROUP BY normalized
                HAVING count(*) > 1
                """
            )
        )
        .all()
    )

    if len(collisions) > 0:
        details = "\n".join(
            f"  {email}: {', '.join(map(str, discord_ids))}"
            for email, discord_ids in collisions
        )

        raise RuntimeError(
            "multiple profiles share the same mailbox, /unverify all but one of them and rerun this migration:\n"
            + details
        )

    op.execute(f"UPDATE profile SET email = {NORMALIZED_EMAIL}")

    op.create_check_constraint(
        "email_no_subaddress",
        "profile",
        "strpos(split_part(email, '@', 1), '+') = 0",
    )


def downgrade() -> None:
    # The stripped subaddresses are not restored
    op.drop_constraint("email_no_subaddress", "profile", type_="check")
