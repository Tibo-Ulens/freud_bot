import logging
import re
import smtplib
import uuid

import discord
from discord import app_commands, Interaction

from bot import constants
from bot.bot import Bot
from bot.decorators import store_command_context, check_has_config_option
from bot.events.verify import EmailEvent, VerifyEvent
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

        email_logger.info(EmailEvent.creating(to))
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.ehlo()
        server.starttls()
        server.login(constants.SMTP_USER, constants.SMTP_PASSWORD)

        server.sendmail(constants.SMTP_USER, to, message)

        server.close()

        email_logger.info(EmailEvent.sent())

    @store_command_context
    async def verify_email(self, ia: Interaction, email: str):
        author_id = ia.user.id
        verification_code = str(uuid.uuid4().hex)

        profile = await Profile.find_by_discord_id(author_id)
        if profile is not None:
            if profile.confirmation_code is None:
                self.bot.logger.warn(VerifyEvent.double_verification(ia.user))
                await ia.response.send_message(
                    VerifyEvent.double_verification(ia.user).user_msg, ephemeral=True
                )
                return
            else:
                self.bot.logger.info(VerifyEvent.code_reset_request(ia.user, email))

                profile.confirmation_code = verification_code
                # Users might have mistyped their email, update it just in case
                profile.email = email
                await profile.save()

                self.send_confirmation_email(email, verification_code)
                await ia.response.send_message(
                    VerifyEvent.code_reset_request(ia.user, email).user_msg,
                    ephemeral=True,
                )

                return

        other = await Profile.find_by_email(email)
        if other is not None:
            self.bot.logger.warn(VerifyEvent.duplicate_email(ia.user))
            await ia.response.send_message(
                VerifyEvent.duplicate_email(ia.user).user_msg,
                ephemeral=True,
            )
            return

        self.bot.logger.info(VerifyEvent.code_request(ia.user, email))
        await Profile.create(
            discord_id=author_id, email=email, confirmation_code=verification_code
        )

        self.send_confirmation_email(email, verification_code)
        await ia.response.send_message(
            VerifyEvent.code_request(ia.user, email).user_msg
        )

    @store_command_context
    async def verify_code(self, ia: Interaction, code: str):
        author_id = ia.user.id
        profile = await Profile.find_by_discord_id(author_id)

        if profile is None:
            self.bot.logger.warn(VerifyEvent.missing_code(ia.user))
            await ia.response.send_message(
                VerifyEvent.missing_code(ia.user).user_msg,
                ephemeral=True,
            )

            return

        if profile.confirmation_code is None:
            self.bot.logger.warn(VerifyEvent.double_verification(ia.user))
            await ia.response.send_message(
                VerifyEvent.double_verification(ia.user).user_msg, ephemeral=True
            )
            return

        stored_code: str = profile.confirmation_code

        if code != stored_code:
            self.bot.logger.warn(VerifyEvent.invalid_code(ia.user))
            await ia.response.send_message(
                VerifyEvent.invalid_code(ia.user).user_msg, ephemeral=True
            )
            return

        user = ia.user

        config = await Config.get(ia.guild_id)
        verified_role = config.verified_role

        await user.add_roles(discord.utils.get(user.guild.roles, id=verified_role))

        profile.confirmation_code = None
        await profile.save()

        self.bot.logger.info(VerifyEvent.verified(ia.user))
        await ia.response.send_message(VerifyEvent.verified(ia.user).user_msg)

    @app_commands.command(
        name="verify", description="Verify that you are a true UGentStudent"
    )
    @app_commands.describe(argument="Your UGent email or verification code")
    @check_has_config_option("verification_channel")
    @check_has_config_option("verified_role")
    @store_command_context
    async def verify(self, ia: Interaction, argument: str):
        config = await Config.get(ia.guild_id)
        verification_channel = config.verification_channel

        if ia.channel_id != verification_channel:
            allowed_channel = discord.utils.get(
                ia.guild.channels, id=verification_channel
            )
            self.bot.logger.warn(
                ModerationEvent.wrong_channel(
                    ia.user, ia.command, ia.channel, allowed_channel
                )
            )
            await ia.response.send_message(
                ModerationEvent.wrong_channel(
                    ia.user, ia.command, ia.channel, allowed_channel
                ).user_msg,
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

        if EMAIL_REGEX.match(msg):
            await self.verify_email(ia, msg)
        elif match := CODE_REGEX.search(msg):
            code = match.group(1)
            await self.verify_code(ia, code)
        else:
            self.bot.logger.warn(VerifyEvent.malformed_argument(ia.user, msg))
            await ia.response.send_message(
                VerifyEvent.malformed_argument(ia.user, msg).user_msg,
                ephemeral=True,
            )


async def setup(bot: Bot):
    await bot.add_cog(Verify(bot))
