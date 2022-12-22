import logging
import re
import smtplib
import traceback
import uuid

import discord
from discord import app_commands, Interaction
from discord.ext.commands import Cog

from bot import constants
from bot.bot import Bot
from bot.models.profile import Profile
from bot.models.config import Config


EMAIL_REGEX = re.compile(r"^[^\s@]+@ugent\.be$")
CODE_REGEX = re.compile(r"^['|<]?([a-z0-9]{32})[>|']?$")

EMAIL_MESSAGE = "From: {from_}\nTo: {to}\nSubject: Psychology Discord Verification Code\n\nYour verification code for the psychology discord server is '{code}'"


logger = logging.getLogger("bot")
email_logger = logging.getLogger("email")


class Verify(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def send_confirmation_email(to: str, code: str):
        message = EMAIL_MESSAGE.format(from_=constants.SMTP_USER, to=to, code=code)

        email_logger.info(f"sending email to {to}...")
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.ehlo()
        server.starttls()
        server.login(constants.SMTP_USER, constants.SMTP_PASSWORD)

        server.sendmail(constants.SMTP_USER, to, message)

        server.close()

        email_logger.info("done")

    async def verify_email(self, iactn: Interaction, email: str):
        author_id = str(iactn.user.id)

        logger.info(f"verifying email '{email}' for [{author_id}] {iactn.user.name}")

        verification_code = str(uuid.uuid4().hex)

        profile = await Profile.find_by_discord_id(author_id)
        if profile is not None:
            if profile.confirmation_code is None:
                logger.info(
                    f"[{author_id}] {iactn.user.name} requested verification for already verified user"
                )
                await iactn.response.send_message(
                    "It seems you are trying to verify again despite already having done so in the past\nIf you think this is a mistake please contact a server admin",
                    ephemeral=True,
                )
                return
            else:
                logger.info(
                    f"[{author_id}] {iactn.user.name} requested verification code reset"
                )

                profile.confirmation_code = verification_code
                await profile.save()

                self.send_confirmation_email(email, verification_code)
                await iactn.response.send_message(
                    f"It seems you had already requested a confirmation code before\nThis code has been revoked and a new one has been sent to '{email}'\nPlease use `/verify <code>` now to complete verification",
                    ephemeral=True,
                )

                return

        other = await Profile.find_by_email(email)
        if other is not None:
            logger.info(
                f"[{author_id}] {iactn.user.name} requested verification for already used email"
            )
            await iactn.response.send_message(
                "A different profile with this email already exists\nIf you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        logger.info(f"[{author_id}] {iactn.user.name} requested new verification code")
        await Profile.create(
            discord_id=author_id, email=email, confirmation_code=verification_code
        )

        self.send_confirmation_email(email, verification_code)
        await iactn.response.send_message(
            f"A confirmation code has been sent to '{email}'\nPlease use `/verify <code>` now to complete verification"
        )

    async def verify_code(self, iactn: Interaction, code: str):
        author_id = str(iactn.user.id)

        logger.info(f"verifying code '{code}' for [{author_id}] {iactn.user.name}")

        profile = await Profile.find_by_discord_id(author_id)

        if profile is None:
            logger.info(
                f"[{author_id}] {iactn.user.name} attempted to verify without requesting a code"
            )
            await iactn.response.send_message(
                "It seems you are trying to verify a code without having requested one first\nPlease use `/verify <email>` to request a code",
                ephemeral=True,
            )

            return

        if profile.confirmation_code is None:
            logger.info(
                f"[{author_id}] {iactn.user.name} attempted to verify again after already having been verified"
            )
            await iactn.response.send_message(
                "It seems you are trying to verify again despite already having done so in the past\nIf you think this is a mistake please contact a server admin",
                ephemeral=True,
            )

            return

        stored_code: str = profile.confirmation_code

        if code != stored_code:
            logger.info(
                f"[{author_id}] {iactn.user.name} attempted to verify with an invalid code"
            )
            await iactn.response.send_message(
                "This verification code is incorrect\nIf you would like to request a new code you may do so by using `/verify <email>`",
                ephemeral=True,
            )

            return

        user = iactn.user

        logger.info(f"[{author_id}] {iactn.user.name} verified succesfully")

        config = await Config.get(iactn.guild_id)
        if config is None:
            logger.error(f"no config for guild {iactn.guild_id} exists yet")
            await iactn.response.send_message(
                "The bot has not been set up properly yet, please notify a server admin"
            )
            return

        verified_role = config.verified_role
        if verified_role is None:
            logger.error(f"no verified role for guild {iactn.guild_id} exists yet")
            await iactn.response.send_message(
                "The bot has not been set up properly yet, please notify a server admin"
            )
            return

        await user.add_roles(discord.utils.get(user.guild.roles, id=int(verified_role)))
        await iactn.response.send_message(
            "You have verified succesfully! Welcome to the server"
        )

        profile.confirmation_code = None
        await profile.save()

    @app_commands.command(
        name="verify", description="Verify that you are a true UGentStudent"
    )
    @app_commands.describe(argument="Your UGent email or verification code")
    async def verify(self, iactn: Interaction, argument: str):
        author_id = iactn.user.id

        config = await Config.get(iactn.guild_id)
        if config is None:
            logger.error(f"no config for guild {iactn.guild_id} exists yet")
            await iactn.response.send_message(
                "The bot has not been set up properly yet, please notify a server admin"
            )
            return

        verification_channel = config.verification_channel
        if verification_channel is None:
            logger.error(
                f"no verification channel for guild {iactn.guild_id} exists yet"
            )
            await iactn.response.send_message(
                "The bot has not been set up properly yet, please notify a server admin"
            )
            return

        if str(iactn.channel_id) != verification_channel:
            await iactn.response.send_message(
                f"This command can only be used in <#{verification_channel}>",
                ephemeral=True,
            )
            return

        msg = argument.strip().lower()

        if len(msg.split(" ")) != 1:
            await iactn.response.send_message(
                "This command only takes one argument\neg. `/verify freud@oedipus.com`\nor `/verify 123456`",
                ephemeral=True,
            )

            return

        try:
            if EMAIL_REGEX.match(msg):
                await self.verify_email(iactn, msg)
            elif match := CODE_REGEX.search(msg):
                code = match.group(1)
                await self.verify_code(iactn, code)
            else:
                logger.info(f"{author_id} submitted invalid email or code: '{msg}'")
                await iactn.response.send_message(
                    "This doesn't look like a valid UGent email or a valid verification code\nIf you think this is a mistake please contact a server admin",
                    ephemeral=True,
                )
        except Exception:
            await iactn.response.send_message(
                "Something went wrong, please notify the server admins"
            )
            logger.error(traceback.format_exc())


async def setup(bot: Bot):
    await bot.add_cog(Verify(bot))
