import logging
import re
import smtplib
import traceback
import uuid

import discord
from discord import app_commands, Interaction

from bot import constants
from bot.bot import Bot
from bot.decorators import store_command_context
from bot.events.verify import EmailEvent, VerifyEvent
from bot.events.config import ConfigEvent
from bot.events.moderation import ModerationEvent
from bot.extensions import ErrorHandledCog
from bot.models.profile import Profile
from bot.models.config import Config


EMAIL_REGEX = re.compile(r"^[^\s@]+@ugent\.be$")
CODE_REGEX = re.compile(r"^['|<]?([a-z0-9]{32})[>|']?$")

EMAIL_MESSAGE = "From: {from_}\nTo: {to}\nSubject: Psychology Discord Verification Code\n\nYour verification code for the psychology discord server is '{code}'"


email_logger = logging.getLogger("email")


class Verify(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def send_confirmation_email(to: str, code: str):
        message = EMAIL_MESSAGE.format(from_=constants.SMTP_USER, to=to, code=code)

        email_logger.info(EmailEvent.Creating(to))
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.ehlo()
        server.starttls()
        server.login(constants.SMTP_USER, constants.SMTP_PASSWORD)

        server.sendmail(constants.SMTP_USER, to, message)

        server.close()

        email_logger.info(EmailEvent.Sent())

    @store_command_context
    async def verify_email(self, ia: Interaction, email: str):
        author_id = ia.user.id
        verification_code = str(uuid.uuid4().hex)

        profile = await Profile.find_by_discord_id(author_id)
        if profile is not None:
            if profile.confirmation_code is None:
                self.bot.logger.warn(VerifyEvent.DoubleVerification(ia.user))
                await ia.response.send_message(
                    VerifyEvent.DoubleVerification(ia.user).human, ephemeral=True
                )
                return
            else:
                self.bot.logger.info(VerifyEvent.CodeResetRequest(ia.user, email))

                profile.confirmation_code = verification_code
                await profile.save()

                self.send_confirmation_email(email, verification_code)
                await ia.response.send_message(
                    VerifyEvent.CodeResetRequest(ia.user, email).human,
                    ephemeral=True,
                )

                return

        other = await Profile.find_by_email(email)
        if other is not None:
            self.bot.logger.warn(VerifyEvent.DuplicateEmail(ia.user))
            await ia.response.send_message(
                VerifyEvent.DuplicateEmail(ia.user).human,
                ephemeral=True,
            )
            return

        self.bot.logger.info(VerifyEvent.CodeRequest(ia.user, email))
        await Profile.create(
            discord_id=author_id, email=email, confirmation_code=verification_code
        )

        self.send_confirmation_email(email, verification_code)
        await ia.response.send_message(VerifyEvent.CodeRequest(ia.user, email).human)

    @store_command_context
    async def verify_code(self, ia: Interaction, code: str):
        author_id = ia.user.id
        profile = await Profile.find_by_discord_id(author_id)

        if profile is None:
            self.bot.logger.warn(VerifyEvent.MissingCode(ia.user))
            await ia.response.send_message(
                VerifyEvent.MissingCode(ia.user).human,
                ephemeral=True,
            )

            return

        if profile.confirmation_code is None:
            self.bot.logger.warn(VerifyEvent.DoubleVerification(ia.user))
            await ia.response.send_message(
                VerifyEvent.DoubleVerification(ia.user).human, ephemeral=True
            )
            return

        stored_code: str = profile.confirmation_code

        if code != stored_code:
            self.bot.logger.warn(VerifyEvent.InvalidCode(ia.user))
            await ia.response.send_message(
                VerifyEvent.InvalidCode(ia.user).human, ephemeral=True
            )
            return

        user = ia.user

        config = await Config.get(ia.guild_id)
        if config is None:
            self.bot.logger.error(ConfigEvent.MissingConfig(ia.guild))
            await ia.response.send_message(ConfigEvent.MissingConfig(ia.guild).human)
            return

        verified_role = config.verified_role
        if verified_role is None:
            self.bot.logger.error(ConfigEvent.MissingVerifiedRole(ia.guild))
            await ia.response.send_message(
                ConfigEvent.MissingVerifiedRole(ia.guild).human
            )
            return

        await user.add_roles(discord.utils.get(user.guild.roles, id=verified_role))

        profile.confirmation_code = None
        await profile.save()

        self.bot.logger.info(VerifyEvent.Verified(ia.user))
        await ia.response.send_message(VerifyEvent.Verified(ia.user).human)

    @app_commands.command(
        name="verify", description="Verify that you are a true UGentStudent"
    )
    @app_commands.describe(argument="Your UGent email or verification code")
    @store_command_context
    async def verify(self, ia: Interaction, argument: str):
        config = await Config.get(ia.guild_id)
        if config is None:
            self.bot.logger.error(ConfigEvent.MissingConfig(ia.guild))
            await ia.response.send_message(ConfigEvent.MissingConfig(ia.guild).human)
            return

        verification_channel = config.verification_channel
        if verification_channel is None:
            self.bot.logger.error(ConfigEvent.MissingVerificationChannel(ia.guild))
            await ia.response.send_message(
                ConfigEvent.MissingVerificationChannel(ia.guild).human
            )
            return

        if ia.channel_id != verification_channel:
            allowed_channel = discord.utils.get(
                ia.guild.channels, id=verification_channel
            )
            self.bot.logger.warn(
                ModerationEvent.WrongChannel(
                    ia.user, ia.command, ia.channel, allowed_channel
                )
            )
            await ia.response.send_message(
                ModerationEvent.WrongChannel(
                    ia.user, ia.command, ia.channel, allowed_channel
                ).human,
                ephemeral=True,
            )
            return

        msg = argument.strip().lower()

        if len(msg.split(" ")) != 1:
            await ia.response.send_message(
                "This command only takes one argument\neg. `/verify freud@oedipus.com`\nor `/verify 123456`",
                ephemeral=True,
            )

            return

        try:
            if EMAIL_REGEX.match(msg):
                await self.verify_email(ia, msg)
            elif match := CODE_REGEX.search(msg):
                code = match.group(1)
                await self.verify_code(ia, code)
            else:
                self.bot.logger.warn(VerifyEvent.MalformedArgument(ia.user, msg))
                await ia.response.send_message(
                    VerifyEvent.MalformedArgument(ia.user, msg).human,
                    ephemeral=True,
                )
        except Exception:
            await ia.response.send_message(
                "Something went wrong, please notify the server admins"
            )
            self.bot.logger.error(traceback.format_exc())


async def setup(bot: Bot):
    await bot.add_cog(Verify(bot))
