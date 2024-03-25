import asyncio
import discord
from discord import app_commands, Interaction, Role, TextChannel, Member
from discord.ext import commands
from discord.ext.commands import command, Context

from models.profile import Profile
from models.config import Config as ConfigModel

from bot import util
from bot.bot import Bot
from bot.decorators import check_user_has_admin_role
from bot.extensions import ErrorHandledCog


class Config(ErrorHandledCog):
    config_group = app_commands.Group(name="config", description="bot configuration")

    config_email_group = app_commands.Group(
        name="email",
        description="verification email configuration",
        parent=config_group,
    )

    @command(name="freudsync")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def sync(self, ctx: Context):
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync()

        self.bot.logger.info(
            f"synced {len(synced)} commmands to {util.render_guild(ctx.guild)}"
        )
        await ctx.reply(f"Synced {len(synced)} commmands to the current guild")

    @app_commands.guild_only()
    @config_group.command(
        name="admin_role",
        description="Set the role that members with admin permissions will have",
    )
    @app_commands.describe(role="The role to be applied")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_admin_role(self, ia: Interaction, role: Role):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.admin_role = role.id
        await guild_config.save()

        self.bot.logger.info(
            f"set admin role for {util.render_guild(ia.guild)} to {util.render_role(role)}"
        )
        await ia.response.send_message(
            f"Set the admin role to {util.render_role(role)}"
        )

    async def refresh_verified_role(self, ia: Interaction, role: Role):
        await ia.response.send_message(
            "New verified role is the same as the old one\nRefreshing role for all verified members...\nThis message will be updated when everything is completed"
        )

        verified_profiles = await Profile.find_verified_in_guild(ia.guild)

        # member_coroutines = []
        # for profile in verified_profiles:
        #     member_coroutines.append(ia.guild.fetch_member(profile.discord_id))

        # members: list[Member] = await asyncio.gather(*member_coroutines)

        members: list[Member] = []
        for profile in verified_profiles:
            members.append(ia.guild.get_member(profile.discord_id))

        role_coroutines = []
        for member in members:
            if member.get_role(role.id) is not None:
                continue

            role_coroutines.append(member.add_roles(role))

        await asyncio.gather(*role_coroutines)

        await ia.edit_original_response(
            content=f"Verified role refreshed, {len(members)} members updated"
        )

    @config_group.command(
        name="verified_role",
        description="Set the role to be applied to members once they have been verified",
    )
    @app_commands.describe(role="The role to be applied")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    async def set_verified_role(self, ia: Interaction, role: Role):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        old_verified_role = None
        if guild_config.verified_role is not None:
            old_verified_role = discord.utils.get(
                ia.guild.roles, id=guild_config.verified_role
            )

        if old_verified_role == role:
            await self.refresh_verified_role(ia, role)
            return

        await ia.response.send_message(
            "Updating verified role...\nThis message will be updated when everything is completed"
        )

        verified_profiles = await Profile.find_verified_in_guild(ia.guild)

        # member_coroutines = []
        # for profile in verified_profiles:
        #     member_coroutines.append(ia.guild.fetch_member(profile.discord_id))

        # members: list[Member] = await asyncio.gather(*member_coroutines)

        members: list[Member] = []
        for profile in verified_profiles:
            members.append(ia.guild.get_member(profile.discord_id))

        role_coroutines = []
        for member in members:
            role_coroutines.append(member.add_roles(role))

            if (
                old_verified_role is not None
                and member.get_role(old_verified_role.id) is not None
            ):
                role_coroutines.append(member.remove_roles(old_verified_role))

        await asyncio.gather(*role_coroutines)

        guild_config.verified_role = role.id
        await guild_config.save()

        self.bot.logger.info(
            f"set verified role for {util.render_guild(ia.guild)} to {util.render_role(role)}, {len(members)} members updated"
        )
        await ia.edit_original_response(
            content=f"Set the verified role to {util.render_role(role)}, {len(members)} members updated"
        )

    @config_group.command(
        name="logging_channel",
        description="Set the channel to which FreudBot logs will be posted",
    )
    @app_commands.describe(channel="The channel to select")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    async def set_logging_channel(self, ia: Interaction, channel: TextChannel):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.logging_channel = channel.id
        await guild_config.save()

        self.bot.logger.info(
            f"set logging channel for {util.render_guild(ia.guild)} to {util.render_channel(channel)}"
        )
        await ia.response.send_message(
            f"Set the logging channel to {util.render_channel(channel)}"
        )

    @config_group.command(
        name="confession_approval_channel",
        description="Set the channel in which FreudBot will post confessions pending approval",
    )
    @app_commands.describe(channel="The channel to select")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    async def set_confession_approval_channel(
        self, ia: Interaction, channel: TextChannel
    ):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.confession_approval_channel = channel.id
        await guild_config.save()

        self.bot.logger.info(
            f"set confession approval channel for {util.render_guild(ia.guild)} to {util.render_channel(channel)}"
        )
        await ia.response.send_message(
            f"Set the confession approval channel to {util.render_channel(channel)}"
        )

    @config_group.command(
        name="confession_channel",
        description="Set the channel to which FreudBot will post approved confessions",
    )
    @app_commands.describe(channel="The channel to select")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    async def set_confession_channel(self, ia: Interaction, channel: TextChannel):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.confession_channel = channel.id
        await guild_config.save()

        self.bot.logger.info(
            f"set confession channel for {util.render_guild(ia.guild)} to {util.render_channel(channel)}"
        )
        await ia.response.send_message(
            f"Set the confession channel to {util.render_channel(channel)}"
        )

    @config_group.command(
        name="email",
        description="Set the email address from which verification emails will be sent",
    )
    @app_commands.describe(
        email="The email address you want to use",
        password="The SMTP password for the email you want to use",
    )
    @app_commands.guild_only()
    @check_user_has_admin_role()
    async def set_verification_email(self, ia: Interaction, email: str, password: str):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        guild_config.verification_email_smtp_user = email
        guild_config.verification_email_smtp_password = password
        await guild_config.save()

        self.bot.logger.info(
            f"set verification email for {util.render_guild(ia.guild)} to {email}"
        )
        await ia.response.send_message(f"Set the verification email to {email}")

    @config_email_group.command(
        name="content", description="Set the content of the verification email"
    )
    @app_commands.describe(
        subject="The subject of the verification email",
        body="The body of the verification email",
    )
    @app_commands.guild_only()
    @check_user_has_admin_role()
    async def set_verification_email_content(
        self, ia: Interaction, subject: str | None = None, body: str | None = None
    ):
        guild_config = await ConfigModel.get_or_create(ia.guild)

        if subject:
            guild_config.verification_email_subject = subject
        if body:
            if body.find("\{code\}") == -1:
                return await ia.response.send_message(
                    "The email body should contain the '\{code\}' variable"
                )

            guild_config.verification_email_body = body

        await guild_config.save()

        self.bot.logger.info(
            f"updated the verification email body for {util.render_guild(ia.guild)}"
        )
        await ia.response.send_message("Verification email subject & body updated")


async def setup(bot: Bot):
    await bot.add_cog(Config(bot))
