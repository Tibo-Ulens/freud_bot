import logging
import re
import smtplib
import uuid

import discord
from discord import app_commands, Interaction, Member, Locale, ButtonStyle, Guild, utils
from discord.ui import View, Button, Modal, TextInput

from models.profile import Profile
from models.config import Config

from bot import constants
from bot.bot import Bot
from bot.decorators import (
    store_command_context,
    check_has_config_option,
    only_in_channel,
)
from bot.exceptions import MissingConfig
from bot.extensions import ErrorHandledCog


EMAIL_REGEX = re.compile(r"^[^\s@]+@ugent\.be$")
CODE_REGEX = re.compile(r"^['|<]?([a-z0-9]{32})[>|']?$")

EMAIL_MESSAGE = "From: {from_}\nTo: {to}\nSubject: Psychology Discord Verification Code\n\nYour verification code for the psychology discord server is '{code}'"


email_logger = logging.getLogger("email")


def send_confirmation_email(to: str, code: str):
    message = EMAIL_MESSAGE.format(from_=constants.SMTP_USER, to=to, code=code)

    email_logger.info(f"creating email to {to}")
    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.ehlo()
    server.starttls()
    server.login(constants.SMTP_USER, constants.SMTP_PASSWORD)

    server.sendmail(constants.SMTP_USER, to, message)

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

    @store_command_context
    async def on_submit(self, ia: Interaction):
        guild_config = await Config.get(self.guild.id)
        if guild_config is None:
            raise MissingConfig(self.guild)

        email = self.email.value

        if not EMAIL_REGEX.match(email):
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with invalid email '{email}'"
            )

            return await ia.response.send_message(
                guild_config.invalid_email_message,
            )

        author_id = ia.user.id
        verification_code = str(uuid.uuid4().hex)

        profile = await Profile.find_by_discord_id(author_id)
        if profile is not None:
            if profile.confirmation_code is None:
                self.bot.discord_logger.warning(
                    f"user {ia.user.mention} attempted to verify despite already being verified"
                )

                return await ia.response.send_message(
                    guild_config.already_verified_message
                )
            else:
                profile.confirmation_code = verification_code
                # Users might have mistyped their email, update it just in case
                profile.email = email
                await profile.save()

                send_confirmation_email(email, verification_code)

                verify_code_view = View(timeout=None)
                verify_code_view.add_item(
                    VerifyCodeButton(
                        guild=self.guild,
                        locale=self.locale,
                        style=ButtonStyle.green,
                        label="verify code",
                    )
                )

                return await ia.response.send_message(
                    guild_config.new_email_message, view=verify_code_view
                )

        other = await Profile.find_by_email(email)
        if other is not None:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with duplicate email {email}"
            )

            return await ia.response.send_message(guild_config.duplicate_email_message)

        self.bot.discord_logger.info(
            f"user {ia.user.mention} requested verification code for {email}"
        )

        await Profile.create(
            discord_id=author_id, email=email, confirmation_code=verification_code
        )

        send_confirmation_email(email, verification_code)

        verify_code_view = View(timeout=None)
        verify_code_view.add_item(
            VerifyCodeButton(
                guild=self.guild,
                locale=self.locale,
            )
        )

        await ia.response.send_message(
            str(guild_config.verify_code_message),
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

    @store_command_context
    async def on_submit(self, ia: Interaction):
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
                f"user {ia.user.mention} attempted to verify despite already being verified"
            )

            return await ia.response.send_message(guild_config.already_verified_message)

        code = ""
        if match := CODE_REGEX.search(self.code.value):
            code = match.group(1)
        else:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with an invalid code"
            )

            return await ia.response.send_message(guild_config.invalid_code_message)

        stored_code: str = profile.confirmation_code

        if code != stored_code:
            self.bot.discord_logger.warning(
                f"user {ia.user.mention} attempted to verify with an invalid code"
            )

            return await ia.response.send_message(guild_config.invalid_code_message)

        verified_role = guild_config.verified_role

        await ia.user.add_roles(discord.utils.get(self.guild.roles, id=verified_role))

        profile.confirmation_code = None
        await profile.save()

        self.bot.discord_logger.info(
            f"{ia.user.mention} verified succesfully with email {profile.email}"
        )

        await ia.response.send_message(
            str(guild_config.welcome_message).format(name=self.guild.name)
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
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="verify", description="Verify that you are a true UGentStudent"
    )
    @only_in_channel("verification_channel")
    @check_has_config_option("verification_channel")
    @check_has_config_option("verified_role")
    @store_command_context
    async def verify(self, ia: Interaction):
        guild_config = await Config.get(ia.guild.id)
        if guild_config is None:
            raise MissingConfig(ia.guild)

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
            content=guild_config.verify_email_message, view=verify_email_view
        )

        return await ia.response.send_message(content="done")

    @ErrorHandledCog.listener("on_member_join")
    async def handle_member_join(self, member: Member):
        if member.bot:
            return

        guild = member.guild

        # Exit if there's no verified role configured yet
        guild_config = await Config.get(guild.id)
        if guild_config is None or guild_config.verified_role is None:
            return

        # Ensure the profile exists
        profile = await Profile.find_by_discord_id(member.id)
        if profile is None:
            return

        # If the profile is already verified somewhere else, verify them here
        # as well
        if profile.email is not None and profile.confirmation_code is None:
            await member.add_roles(
                discord.utils.get(guild.roles, id=guild_config.verified_role)
            )
            return

        # If the profile is not verified yet send them through the
        # verification process
        dm_channel = member.dm_channel
        if dm_channel is None:
            dm_channel = await member.create_dm()

        verify_email_view = View(timeout=None)
        verify_email_view.add_item(
            VerifyEmailButton(bot=self.bot, guild=guild, locale=guild.preferred_locale)
        )

        dm_channel.send(
            content=guild_config.verify_email_message,
            view=verify_email_view,
        )


async def setup(bot: Bot):
    await bot.add_cog(Verification(bot))
