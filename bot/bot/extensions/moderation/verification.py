import asyncio

import discord
from discord import app_commands, Interaction, Member

from models.profile import VerifiedProfile
from models.config import Config

from bot.bot import Bot
from bot.decorators import (
    check_has_config_option,
    check_user_has_admin_role,
)
from bot.exceptions import MissingConfig, MissingConfigOption
from bot.extensions import ErrorHandledCog


class Verification(ErrorHandledCog):
    @app_commands.command(
        name="verifix",
        description="Check that every verified member has the verified role",
    )
    @app_commands.guild_only()
    @check_has_config_option("verified_role")
    @check_user_has_admin_role()
    async def verifix(self, ia: Interaction):
        guild_config = await Config.get(ia.guild_id)
        verified_role = discord.utils.get(
            ia.guild.roles, id=int(guild_config.verified_role)
        )

        await ia.response.send_message(
            "Checking members...\nThis message will be updated when everything is completed"
        )

        verified_profiles = await VerifiedProfile.find_in_guild(ia.guild)

        members: list[Member] = [
            ia.guild.get_member(int(profile.discord_id))
            for profile in verified_profiles
        ]

        role_coroutines = []
        not_updated = 0
        for member in members:
            if member.get_role(verified_role.id) is not None:
                not_updated += 1
                continue

            role_coroutines.append(member.add_roles(verified_role))

        await asyncio.gather(*role_coroutines)

        await ia.edit_original_response(
            content=f"{len(members)} verified members checked, {len(members) - not_updated} members updated"
        )

    @app_commands.command(
        name="unverify", description="Remove somebody from the verified users database"
    )
    @app_commands.describe(user="The user to unverify")
    @app_commands.guild_only()
    async def unverify(self, ia: Interaction, user: Member):
        guild_config = await Config.get(ia.guild.id)
        if guild_config is None:
            raise MissingConfig(ia.guild)

        await ia.response.defer(ephemeral=True, thinking=True)

        profile = await VerifiedProfile.find_by_discord_id(user.id)
        if profile:
            await profile.delete()

        if guild_config.verified_role:
            verified_role = discord.utils.get(
                ia.guild.roles, id=guild_config.verified_role
            )
            if verified_role:
                await user.remove_roles(verified_role)

        self.bot.discord_logger.info(
            f"{user.mention} was unverified manually",
            guild=ia.guild,
            log_type="verification",
        )

        return await ia.followup.send("done")

    @ErrorHandledCog.listener("on_member_join")
    async def handle_member_join(self, member: Member):
        if member.bot:
            return

        guild = member.guild

        # Exit if there's no verified role configured yet
        guild_config = await Config.get(guild.id)
        if guild_config is None:
            raise MissingConfig(guild)
        if guild_config.verified_role is None:
            raise MissingConfigOption("verified_role")

        verified_profile = await VerifiedProfile.find_by_discord_id(member.id)

        # If the profile is already verified somewhere else, verify them here
        # as well
        if verified_profile is not None:
            await member.add_roles(
                discord.utils.get(guild.roles, id=guild_config.verified_role)
            )

            self.bot.discord_logger.info(
                f"{member.mention} [{verified_profile.email}] has been automatically verified",
                guild=guild,
                log_type="verification",
            )

            return

        self.bot.logger.info(
            f"sending verification DM to {member.mention} [{member.name}]"
        )

        # If the profile is not verified yet send them to the website
        dm_channel = member.dm_channel
        if dm_channel is None:
            dm_channel = await member.create_dm()

        await dm_channel.send(
            content=str(guild_config.verify_email_message).format(guild_name=guild.name)
        )


async def setup(bot: Bot):
    await bot.add_cog(Verification(bot))
