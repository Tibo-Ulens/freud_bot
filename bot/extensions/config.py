from discord import app_commands, Interaction, Role, TextChannel
from discord.ext import commands
from discord.ext.commands import Cog, command, Context
import logging

from bot.bot import Bot
from bot.events.config import Config as ConfigEvent
from bot.models.config import Config as ConfigModel
from bot.util import has_admin_role, render_role, render_channel


logger = logging.getLogger("bot")


class Config(Cog):
    config_group = app_commands.Group(name="config", description="bot configuration")

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="freudsync")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def sync(self, ctx: Context):
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync()

        logger.info(ConfigEvent.SyncedCommands(ctx.guild, len(synced)))
        await ctx.reply(ConfigEvent.SyncedCommands(ctx.guild, len(synced)).human)

    @app_commands.guild_only()
    @has_admin_role()
    @config_group.command(
        name="verified_role",
        description="Set the role to be applied to members once they have been verified",
    )
    @app_commands.describe(role="The role to be applied")
    async def set_verified_role(self, ia: Interaction, role: Role):
        guild_config = await ConfigModel.get_or_create(ia.guild_id)

        guild_config.verified_role = str(role.id)
        await guild_config.save()

        logger.info(ConfigEvent.SetVerifiedRole(ia.guild, role))
        await ia.response.send_message(
            ConfigEvent.SetVerifiedRole(ia.guild, role).human
        )

    @app_commands.guild_only()
    @has_admin_role()
    @config_group.command(
        name="verification_channel",
        description="Set the channel in which the /verify command can be used",
    )
    @app_commands.describe(channel="The channel to select")
    async def set_verification_channel(self, ia: Interaction, channel: TextChannel):
        guild_config = await ConfigModel.get_or_create(ia.guild_id)

        guild_config.verification_channel = str(channel.id)
        await guild_config.save()

        logger.info(ConfigEvent.SetVerificationChannel(ia.guild, channel))
        await ia.response.send_message(
            ConfigEvent.SetVerificationChannel(ia.guild, channel).human
        )

    @app_commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @config_group.command(
        name="admin_role",
        description="Set the role that members with admin permissions will have",
    )
    @app_commands.describe(role="The role to be applied")
    async def set_admin_role(self, ia: Interaction, role: Role):
        guild_config = await ConfigModel.get_or_create(ia.guild_id)

        guild_config.admin_role = str(role.id)
        await guild_config.save()

        logger.info(ConfigEvent.SetAdminRole(ia.guild, role))
        await ia.response.send_message(ConfigEvent.SetAdminRole(ia.guild, role).human)


async def setup(bot: Bot):
    await bot.add_cog(Config(bot))
