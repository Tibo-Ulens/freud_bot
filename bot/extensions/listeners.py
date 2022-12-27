import random
import logging

import discord
from discord import Message, Guild, Member
from discord.ext.commands import Cog

from bot import constants, root_logger
from bot.bot import Bot
from bot.events.bot import BotEvent as BotEvent
from bot.discord_logger import DiscordHandler
from bot.models.config import Config
from bot.models.profile import Profile


logger = logging.getLogger("bot")


class Listeners(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        logger.info(BotEvent.Ready())

    @Cog.listener()
    async def on_guild_available(self, guild: Guild):
        logger.info(f"guild {guild.name} available")

        guild_config = await Config.get(guild.id)
        if guild_config is None or guild_config.logging_channel is None:
            return

        logging_channel = guild.get_channel(guild_config.logging_channel)
        discord_handler = DiscordHandler(channel=logging_channel, filter_target="bot")
        self.bot.discord_handler = discord_handler
        root_logger.addHandler(discord_handler)

    @Cog.listener()
    async def on_message(self, msg: Message):
        if self.bot.user in msg.mentions:
            quote = random.choice(constants.FREUD_QUOTES)
            await msg.reply(quote)

    @Cog.listener()
    async def on_member_join(self, member: Member):
        guild = member.guild

        guild_config = await Config.get(member.id)
        if guild_config is None or guild_config.verified_role is None:
            return

        profile = await Profile.find_by_discord_id(member.id)
        if profile is None:
            return

        if profile.email is not None and profile.confirmation_code is None:
            await member.add_roles(
                discord.utils.get(guild.roles, id=guild_config.verified_role)
            )


async def setup(bot: Bot):
    await bot.add_cog(Listeners(bot))
