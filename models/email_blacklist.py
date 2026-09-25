from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Text, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.schema import FetchedValue

from models import Base, Model, session_factory
from models.profile import normalize_email


class EmailBlacklist(Base, Model):
    """Emails that are not allowed to receive the verified role in a guild"""

    __tablename__ = "email_blacklist"

    guild_id = Column(BigInteger, ForeignKey("config.guild_id"), primary_key=True)
    email = Column(Text, primary_key=True)
    banned_discord_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), FetchedValue(), nullable=False)

    def __repr__(self) -> str:
        return f"EmailBlacklist(guild_id={self.guild_id}, email={self.email}, banned_discord_id={self.banned_discord_id})"

    @classmethod
    async def is_blacklisted(cls, guild_id: int, email: str) -> bool:
        """Check if an email is blacklisted in a given guild"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(
                    cls.guild_id == guild_id, cls.email == normalize_email(email)
                )
            )

            return result.first() is not None

    @classmethod
    async def add(
        cls, guild_id: int, email: str, banned_discord_id: int | None = None
    ) -> bool:
        """
        Blacklist an email in a given guild

        Returns False if it was already blacklisted
        """

        async with session_factory() as session:
            result: Result = await session.execute(
                insert(cls)
                .values(
                    guild_id=guild_id,
                    email=normalize_email(email),
                    banned_discord_id=banned_discord_id,
                )
                .on_conflict_do_nothing()
            )
            await session.commit()

            return result.rowcount > 0

    @classmethod
    async def remove(cls, guild_id: int, email: str) -> bool:
        """
        Remove an email from a guilds blacklist

        Returns False if it wasn't blacklisted
        """

        async with session_factory() as session:
            result: Result = await session.execute(
                delete(cls).where(
                    cls.guild_id == guild_id, cls.email == normalize_email(email)
                )
            )
            await session.commit()

            return result.rowcount > 0

    @classmethod
    async def remove_ban(cls, guild_id: int, discord_id: int) -> list[str]:
        """
        Remove the entries that were created by banning a given account

        Returns the emails that were removed
        """

        async with session_factory() as session:
            result: Result = await session.execute(
                delete(cls)
                .where(cls.guild_id == guild_id, cls.banned_discord_id == discord_id)
                .returning(cls.email)
            )
            await session.commit()

            return list(result.scalars().all())

    @classmethod
    async def get_for_guild(cls, guild_id: int) -> list["EmailBlacklist"]:
        """Get the blacklist of a given guild, newest first"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls)
                .where(cls.guild_id == guild_id)
                .order_by(cls.created_at.desc())
            )

            return result.scalars().all()
