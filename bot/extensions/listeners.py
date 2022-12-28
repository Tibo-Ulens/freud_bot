import random
import logging

import discord
from discord import Message, Guild, Member

from bot import constants, root_logger
from bot.bot import Bot
from bot.events.bot import BotEvent as BotEvent
from bot.extensions import ErrorHandledCog
from bot.log.discord_handler import DiscordHandler
from bot.log.guild_adapter import GuildAdapter
from bot.models.config import Config
from bot.models.profile import Profile


logger = logging.getLogger("bot")


class Listeners(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @ErrorHandledCog.listener()
    async def on_ready(self):
        bot_logger = root_logger.getChild("bot")
        bot_logger.addHandler(DiscordHandler(filter_target="bot"))

        logger_ = GuildAdapter(bot_logger)
        self.bot.logger = logger_

        logger.info(BotEvent.Ready())

    @ErrorHandledCog.listener()
    async def on_guild_available(self, guild: Guild):
        logger.info(f"guild {guild.name} available")

    @ErrorHandledCog.listener()
    async def on_message(self, msg: Message):
        if self.bot.user in msg.mentions:
            quote = random.choice(constants.FREUD_QUOTES)
            await msg.reply(quote)

    @ErrorHandledCog.listener()
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
