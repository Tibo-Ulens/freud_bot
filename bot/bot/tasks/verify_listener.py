import asyncio
from discord import Guild
from discord.abc import Snowflake
import logging

from bot.bot import Bot
from models.config import Config


logger = logging.getLogger("queue")


async def verify_member_in_guild(user_id: Snowflake, guild: Guild, bot: Bot):
    guild_config = await Config.get(guild.id)
    if guild_config is None:
        return

    verified_role_id = guild_config.verified_role
    if verified_role_id is None:
        return

    verified_role = guild.get_role(verified_role_id)
    if verified_role is None:
        return

    member = guild.get_member(user_id)
    if member is None:
        return

    await member.add_roles(verified_role)

    logger.info(
        f"verified user [{member.name} - {member.id}] in guild [{guild.name} - {guild.id}]"
    )

    bot.discord_logger.info(
        f"{user_id} verified succesfully",
        guild=guild,
        log_type="verification",
    )


async def verify_listener(bot: Bot):
    channel = await bot.pika.channel()
    queue = await channel.declare_queue("verification")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                user_id = int.from_bytes(message.body, "little")

                logger.info(f"got verification command for user {user_id}")

                verify_coros = [
                    verify_member_in_guild(user_id, g, bot) for g in bot.guilds
                ]
                await asyncio.gather(*verify_coros)


async def setup(bot: Bot):
    bot.loop.create_task(verify_listener(bot))
