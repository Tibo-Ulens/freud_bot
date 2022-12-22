from discord import app_commands, Interaction, Role, TextChannel
from discord.ext import commands
from discord.ext.commands import Cog, command, Context
import logging

from bot.bot import Bot
from bot.models.config import Config as ConfigModel
from bot import constants


logger = logging.getLogger("bot")


class Config(Cog):
    config_group = app_commands.Group(name="config", description="bot configuration")

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="freud_sync")
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context):
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync(guild=ctx.guild)

        logger.info(f"synced {len(synced)} commands to {ctx.guild.name}")
        await ctx.reply(f"synced {len(synced)} commands to the current guild")

    @app_commands.guild_only()
    @config_group.command(
        name="verified_role",
        description="Set the role to be applied to members once they have been verified",
    )
    @app_commands.describe(role="The role to be applied")
    async def set_verified_role(self, ia: Interaction, role: Role):
        guild_config = await ConfigModel.get_or_create(ia.guild_id)

        guild_config.verified_role = str(role.id)
        await guild_config.save()

        logger.info(f"set verified role to {role.id} for guild {ia.guild_id}")
        await ia.response.send_message(f"set verified role to <@&{role.id}>")

    @app_commands.guild_only()
    @config_group.command(
        name="verification_channel",
        description="Set the channel in which the /verify command can be used",
    )
    @app_commands.describe(channel="The channel to select")
    async def set_verification_channel(self, ia: Interaction, channel: TextChannel):
        guild_config = await ConfigModel.get_or_create(ia.guild_id)

        guild_config.verification_channel = str(channel.id)
        await guild_config.save()

        logger.info(f"set verification channel to {channel.id} for guild {ia.guild_id}")
        await ia.response.send_message(f"set verification channel to <#{channel.id}>")


async def setup(bot: Bot):
    await bot.add_cog(Config(bot))
