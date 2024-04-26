import asyncio
import logging
import re
import smtplib
import uuid

import discord
from discord import app_commands, Interaction, Member, Locale, ButtonStyle, Guild
from discord.ui import View, Button, Modal, TextInput

from models import profile_statistics
from models.profile import Profile
from models.config import Config

from bot.bot import Bot
from bot.decorators import (
    check_has_config_option,
    check_user_has_admin_role,
)
from bot.exceptions import MissingConfig, MissingConfigOption
from bot.extensions import ErrorHandledCog
from models.profile_statistics import ProfileStatistics


EMAIL_REGEX = re.compile(r"^[^\s@]+@ugent\.be$")
CODE_REGEX = re.compile(r"^['|<]?([a-z0-9]{32})[>|']?$")

EMAIL_MESSAGE = "From: {from_}\nTo: {to}\nSubject: {subject}\n\n{body}"


email_logger = logging.getLogger("email")


def send_confirmation_email(
    from_: str, password: str, to: str, subject: str, body: str, code: str
):
    actual_body = body.format(code=code)
    message = EMAIL_MESSAGE.format(
        from_=from_, to=to, subject=subject, body=actual_body
    )

    email_logger.info(f"creating email to {to}")
    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.ehlo()
    server.starttls()
    server.login(from_, password)

    server.sendmail(from_, to, message)

    server.close()

    email_logger.info(f"sent email to {to}")


class VerifyEmailModal(Modal):
    email = TextInput(label="email", placeholder="jan.peeters@ugent.be")

    def __init__(self, bot: Bot, guild: Guild, locale: Locale) -> None:
        self.bot = bot
        self.guild = guild
        self.locale = locale

        title = "Verifieer je email" if locale == Locale.dutch else "Verify your email"

        super().__init__(title=title, timeout=None)

    async def on_submit(self, ia: Interaction):
        guild_config = await Config.get(self.guild.id)
        if guild_config is None:
            raise MissingConfig(self.guild)

        email = self.email.value.lower()

        if not EMAIL_REGEX.match(email):
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with invalid email '{email}'",
                guild=self.guild,
                log_type="verification",
            )

            return await ia.response.send_message(
                str(guild_config.invalid_email_message).format(email=email),
            )

        author_id = ia.user.id
        verification_code = str(uuid.uuid4().hex)

        profile = await Profile.find_by_discord_id(author_id)
        if profile is not None:
            if profile.confirmation_code is None:
                self.bot.discord_logger.warning(
                    f"user {ia.user.mention} attempted to verify despite already being verified",
                    guild=self.guild,
                    log_type="verification",
                )

                return await ia.response.send_message(
                    guild_config.already_verified_message
                )

            profile.confirmation_code = verification_code
            # Users might have mistyped their email, update it just in case
            old = profile.email
            profile.email = email
            await profile.save()

            send_confirmation_email(
                guild_config.verification_email_smtp_user,
                guild_config.verification_email_smtp_password,
                email,
                guild_config.verification_email_subject,
                guild_config.verification_email_body,
                verification_code,
            )

            verify_code_view = View(timeout=None)
            verify_code_view.add_item(
                VerifyCodeButton(
                    bot=self.bot,
                    guild=self.guild,
                    locale=self.locale,
                )
            )

            self.bot.discord_logger.info(
                f"user {ia.user.mention} re-requested a verification code for '{email}'",
                guild=self.guild,
                log_type="verification",
            )

            return await ia.response.send_message(
                str(guild_config.new_email_message).format(old=old, new=email),
                view=verify_code_view,
            )

        other = await Profile.find_by_email(email)
        if other is not None:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with duplicate email '{email}'\ntheir other account is <@{other.discord_id}>",
                guild=self.guild,
                log_type="verification",
            )

            return await ia.response.send_message(
                str(guild_config.duplicate_email_message).format(email=email)
            )

        self.bot.discord_logger.info(
            f"user {ia.user.mention} requested verification code for '{email}'",
            guild=self.guild,
            log_type="verification",
        )

        await Profile.create(
            discord_id=author_id, email=email, confirmation_code=verification_code
        )

        send_confirmation_email(
            guild_config.verification_email_smtp_user,
            guild_config.verification_email_smtp_password,
            email,
            guild_config.verification_email_subject,
            guild_config.verification_email_body,
            verification_code,
        )

        verify_code_view = View(timeout=None)
        verify_code_view.add_item(
            VerifyCodeButton(
                bot=self.bot,
                guild=self.guild,
                locale=self.locale,
            )
        )

        return await ia.response.send_message(
            str(guild_config.verify_code_message).format(email=email),
            view=verify_code_view,
        )


class VerifyCodeModal(Modal):
    code = TextInput(label="code", placeholder="1234567890")

    def __init__(self, bot: Bot, guild: Guild, locale: Locale) -> None:
        self.bot = bot
        self.guild = guild
        self.locale = locale

        title = (
            "Check je verificatie code"
            if locale == Locale.dutch
            else "Check your verification code"
        )

        super().__init__(title=title, timeout=None)

    async def on_submit(self, ia: Interaction):
        await ia.response.defer(thinking=True)

        author_id = ia.user.id
        profile = await Profile.find_by_discord_id(author_id)

        guild_config = await Config.get(self.guild.id)
        if guild_config is None:
            raise MissingConfig(self.guild)

        if profile is None:
            # This should not be reachable
            # Users cannot access this modal without first sending in their email
            raise Exception()

        if profile.confirmation_code is None:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify despite already being verified",
                guild=self.guild,
                log_type="verification",
            )

            return await ia.followup.send(guild_config.already_verified_message)

        code = ""
        if match := CODE_REGEX.search(self.code.value):
            code = match.group(1)
        else:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with an invalid code '{self.code.value}', invalid pattern",
                guild=self.guild,
                log_type="verification",
            )

            return await ia.followup.send(
                str(guild_config.invalid_code_message).format(code=self.code.value)
            )

        stored_code: str = profile.confirmation_code

        if code != stored_code:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with an invalid code '{code}', expected '{stored_code}'",
                guild=self.guild,
                log_type="verification",
            )

            return await ia.followup.send(
                str(guild_config.invalid_code_message).format(code=code)
            )

        async def verify_member_in_guild(guild: Guild):
            guild_config = await Config.get(guild.id)
            if guild_config is None:
                return

            verified_role = guild_config.verified_role
            if verified_role is None:
                return

            member = guild.get_member(ia.user.id)
            if member is None:
                return

            await member.add_roles(guild.get_role(verified_role))

            await ProfileStatistics.create(
                profile_discord_id=ia.user.id, config_guild_id=guild.id
            )

            self.bot.discord_logger.info(
                f"{ia.user.mention} verified succesfully with email {profile.email} from within server '{self.guild.name}'",
                guild=guild,
                log_type="verification",
            )

        # Verify the user in the guild they used the command in
        verified_role = guild_config.verified_role
        member = self.guild.get_member(ia.user.id)

        await member.add_roles(self.guild.get_role(verified_role))

        profile.confirmation_code = None
        await profile.save()

        await ProfileStatistics.create(
            profile_discord_id=ia.user.id, config_guild_id=self.guild.id
        )

        self.bot.discord_logger.info(
            f"{ia.user.mention} verified succesfully with email '{profile.email}'",
            guild=self.guild,
            log_type="verification",
        )

        # Verify the user in any other freud-enabled guilds
        other_guilds = list(filter(lambda g: g.id != self.guild.id, self.bot.guilds))
        other_guild_coroutines = [verify_member_in_guild(g) for g in other_guilds]
        await asyncio.gather(*other_guild_coroutines)

        return await ia.followup.send(
            str(guild_config.welcome_message).format(guild_name=self.guild.name)
        )


class VerifyEmailButton(Button):
    def __init__(self, bot: Bot, guild: Guild, locale: Locale, *args, **kwargs):
        self.bot = bot
        self.guild = guild
        self.locale = locale

        label = "Verifieer je email" if locale == Locale.dutch else "Verify your email"

        super().__init__(*args, style=ButtonStyle.green, label=label, **kwargs)

    async def callback(self, ia: Interaction):
        await ia.response.send_modal(
            VerifyEmailModal(bot=self.bot, guild=self.guild, locale=ia.locale)
        )


class VerifyCodeButton(Button):
    def __init__(self, bot: Bot, guild: Guild, locale: Locale, *args, **kwargs):
        self.bot = bot
        self.guild = guild
        self.locale = locale

        label = "Verifieer je code" if locale == Locale.dutch else "Verify your code"

        super().__init__(*args, style=ButtonStyle.green, label=label, **kwargs)

    async def callback(self, ia: Interaction):
        await ia.response.send_modal(
            VerifyCodeModal(bot=self.bot, guild=self.guild, locale=self.locale)
        )


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
        verified_role = discord.utils.get(ia.guild.roles, id=guild_config.verified_role)

        await ia.response.send_message(
            "Checking members...\nThis message will be updated when everything is completed"
        )

        verified_profiles = await Profile.find_verified_in_guild(ia.guild)

        members: list[Member] = []
        for profile in verified_profiles:
            members.append(ia.guild.get_member(profile.discord_id))

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
        name="verify", description="Verify that you are a true UGentStudent"
    )
    @app_commands.guild_only()
    @check_has_config_option("verified_role")
    @check_has_config_option("verification_email_smtp_user")
    @check_has_config_option("verification_email_smtp_password")
    async def verify(self, ia: Interaction):
        guild_config = await Config.get(ia.guild.id)
        if guild_config is None:
            raise MissingConfig(ia.guild)

        await ia.response.defer(ephemeral=True, thinking=True)

        profile = await Profile.find_by_discord_id(ia.user.id)
        if profile is not None and profile.confirmation_code is None:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify despite already being verified",
                guild=ia.guild,
                log_type="verification",
            )

            return await ia.followup.send(guild_config.already_verified_message)

        verify_email_view = View(timeout=None)
        verify_email_view.add_item(
            VerifyEmailButton(bot=self.bot, guild=ia.guild, locale=ia.locale)
        )

        dm_channel = (
            ia.user.dm_channel
            if ia.user.dm_channel is not None
            else await ia.user.create_dm()
        )

        await dm_channel.send(
            content=str(guild_config.verify_email_message).format(
                guild_name=ia.guild.name
            ),
            view=verify_email_view,
        )

        msg = (
            "Er is een DM verstuurd naar je met verdere instructies"
            if ia.locale == Locale.dutch
            else "You have received a DM with further instructions"
        )

        return await ia.followup.send(content=msg, ephemeral=True)

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

        profile_statistics = await ProfileStatistics.get_all_for_user(user.id)
        stat_futures = [stat.delete() for stat in profile_statistics]
        await asyncio.gather(*stat_futures)

        profile = await Profile.find_by_discord_id(user.id)
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
            guild=self.guild,
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
        if guild_config.verification_email_smtp_user is None:
            raise MissingConfigOption("verification_email_smtp_user")
        if guild_config.verification_email_smtp_password is None:
            raise MissingConfigOption("verification_email_smtp_password")

        profile = await Profile.find_by_discord_id(member.id)

        # If the profile is already verified somewhere else, verify them here
        # as well
        if (
            profile is not None
            and profile.email is not None
            and profile.confirmation_code is None
        ):
            await member.add_roles(
                discord.utils.get(guild.roles, id=guild_config.verified_role)
            )

            await ProfileStatistics.create(
                profile_discord_id=member.id, config_guild_id=guild.id
            )

            self.bot.discord_logger.info(
                f"{member.mention} has been automatically verified, their email is {profile.email}",
                guild=guild,
                log_type="verification",
            )

            return

        self.bot.logger.info(
            f"sending verification DM to {member.mention} [{member.name}]"
        )

        # If the profile is not verified yet send them through the
        # verification process
        dm_channel = member.dm_channel
        if dm_channel is None:
            dm_channel = await member.create_dm()

        verify_email_view = View(timeout=None)
        verify_email_view.add_item(
            VerifyEmailButton(bot=self.bot, guild=guild, locale=guild.preferred_locale)
        )

        await dm_channel.send(
            content=str(guild_config.verify_email_message).format(
                guild_name=guild.name
            ),
            view=verify_email_view,
        )


async def setup(bot: Bot):
    await bot.add_cog(Verification(bot))
