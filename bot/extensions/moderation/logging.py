import logging

import discord
from discord import Message, Guild

from models.config import Config

from bot import root_logger, util
from bot.bot import Bot
from bot.extensions import ErrorHandledCog
from bot.log.discord_handler import DiscordHandler
from bot.log.guild_adapter import GuildAdapter


logger = logging.getLogger("bot")


MSG = """
This does not seem to be a valid `/verify` command, did you use the autocomplete prompt?

Normally you should get an autocomplete prompt when you start typing `/verify`.
You can select this prompt by fully typing out `/verify` and then a space, by pressing tab, or by clicking on the prompt.

If you experience further issues, please contact somebody that looks important.
"""


class ModLogging(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @ErrorHandledCog.listener()
    async def on_ready(self):
        discord_logger = logging.getLogger("discord")
        discord_logger.addHandler(DiscordHandler(filter_target="discord"))

        discord_logger_ = GuildAdapter(discord_logger)
        self.bot.discord_logger = discord_logger_

        logger_ = root_logger.getChild("bot")
        self.bot.logger = logger_

        logger.info("ready")

    @ErrorHandledCog.listener()
    async def on_guild_available(self, guild: Guild):
        logger.info(f"guild {util.render_guild(guild)} available")

    @ErrorHandledCog.listener()
    async def on_guild_join(self, guild: Guild):
        logger.info(f"joined guild {util.render_guild(guild)}")
        await Config.create(guild_id=guild.id)
        logger.info(f"created config for guild {util.render_guild(guild)}")

    @ErrorHandledCog.listener()
    async def on_message(self, msg: Message):
        if msg.author == self.bot.user:
            return

        guild_config = await Config.get(msg.guild.id)
        if (
            guild_config is not None
            and guild_config.verification_channel is not None
            and msg.channel.id == guild_config.verification_channel
        ):
            if (
                guild_config.admin_role is not None
                and discord.utils.get(msg.guild.roles, id=guild_config.admin_role)
                in msg.author.roles
            ):
                return

            await msg.reply(MSG)


async def setup(bot: Bot):
    await bot.add_cog(ModLogging(bot))
