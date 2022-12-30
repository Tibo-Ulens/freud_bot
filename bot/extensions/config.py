import asyncio
import discord
from discord import app_commands, Interaction, Role, TextChannel, Member
from discord.ext import commands
from discord.ext.commands import command, Context

from bot.bot import Bot
from bot.decorators import check_user_has_admin_role, store_command_context
from bot.extensions import ErrorHandledCog
from bot.events.config import ConfigEvent
from bot.models.profile import Profile
from bot.models.config import Config as ConfigModel


class Config(ErrorHandledCog):
    config_group = app_commands.Group(name="config", description="bot configuration")

    @command(name="freudsync")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @store_command_context
    async def sync(self, ctx: Context):
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync()

        self.bot.logger.info(ConfigEvent.SyncedCommands(ctx.guild, len(synced)))
        await ctx.reply(ConfigEvent.SyncedCommands(ctx.guild, len(synced)).human)

    @app_commands.guild_only()
    @config_group.command(
        name="admin_role",
        description="Set the role that members with admin permissions will have",
    )
    @app_commands.describe(role="The role to be applied")
    @commands.has_guild_permissions(manage_guild=True)
    @store_command_context
    async def set_admin_role(self, ia: Interaction, role: Role):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.admin_role = role.id
        await guild_config.save()

        self.bot.logger.info(ConfigEvent.SetAdminRole(ia.guild, role))
        await ia.response.send_message(ConfigEvent.SetAdminRole(ia.guild, role).human)

    @config_group.command(
        name="verified_role",
        description="Set the role to be applied to members once they have been verified",
    )
    @app_commands.describe(role="The role to be applied")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    @store_command_context
    async def set_verified_role(self, ia: Interaction, role: Role):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        old_verified_role = None
        if guild_config.verified_role is not None:
            old_verified_role = discord.utils.get(
                ia.guild.roles, id=guild_config.verified_role
            )

        verified_profiles = await Profile.find_verified_in_guild(ia.guild)

        member_coroutines = []
        for profile in verified_profiles:
            member_coroutines.append(ia.guild.fetch_member(profile.discord_id))
        members: list[Member] = await asyncio.gather(*member_coroutines)

        role_coroutines = []
        for member in members:
            role_coroutines.append(member.add_roles(role))
            if old_verified_role is not None:
                role_coroutines.append(member.remove_roles(old_verified_role))
        await asyncio.gather(*role_coroutines)

        guild_config.verified_role = role.id
        await guild_config.save()

        self.bot.logger.info(ConfigEvent.SetVerifiedRole(ia.guild, role, len(members)))
        await ia.response.send_message(
            ConfigEvent.SetVerifiedRole(ia.guild, role, len(members)).human
        )

    @config_group.command(
        name="verification_channel",
        description="Set the channel in which the /verify command can be used",
    )
    @app_commands.describe(channel="The channel to select")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    @store_command_context
    async def set_verification_channel(self, ia: Interaction, channel: TextChannel):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.verification_channel = channel.id
        await guild_config.save()

        self.bot.logger.info(ConfigEvent.SetVerificationChannel(ia.guild, channel))
        await ia.response.send_message(
            ConfigEvent.SetVerificationChannel(ia.guild, channel).human
        )

    @config_group.command(
        name="logging_channel",
        description="Set the channel to which FreudBot logs will be posted",
    )
    @app_commands.describe(channel="The channel to select")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    @store_command_context
    async def set_logging_channel(self, ia: Interaction, channel: TextChannel):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.logging_channel = channel.id
        await guild_config.save()

        self.bot.logger.info(ConfigEvent.SetLoggingChannel(ia.guild, channel))
        await ia.response.send_message(
            ConfigEvent.SetLoggingChannel(ia.guild, channel).human
        )


async def setup(bot: Bot):
    await bot.add_cog(Config(bot))
