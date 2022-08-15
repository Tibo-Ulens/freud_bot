import logging
import re
import smtplib
import traceback
import uuid

from typing import Optional

import discord
from discord.ext.commands import Cog, Context, command

from bot import constants
from bot.bot import Bot


EMAIL_REGEX = re.compile(r"[^\s@]+@ugent\.be")

EMAIL_USER = "psychology.ugent@gmail.com"
EMAIL_MESSAGE = "From: psychology.ugent@gmail.com\nTo: {to}\nSubject: Psychology Discord Verification Code\n\nYour verification code for the psychology discord server is '{code}'"

FIND_USER_QUERY = "SELECT * FROM verified_user WHERE discord_id = '{id}';"
UPDATE_USER_QUERY = (
    "UPDATE verified_user SET confirmation_code = '{code}' WHERE discord_id = '{id}';"
)
INSERT_USER_QUERY = "INSERT INTO verified_user VALUES ({id}, '{email}', '{code}');"
VERIFY_USER_QUERY = (
    "UPDATE verified_user SET confirmation_code = NULL WHERE discord_id = '{id}';"
)


logger = logging.getLogger("bot")
email_logger = logging.getLogger("email")


class Verify(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def send_confirmation_email(to: str, code: str):
        message = EMAIL_MESSAGE.format(to=to, code=code)

        email_logger.info(f"sending email to {to}")
        server = smtplib.SMTP("smtp.gmail.com", 587)

        email_logger.info("sending ehlo...")
        server.ehlo()

        email_logger.info("switching to TLS...")
        server.starttls()

        email_logger.info("logging in...")
        server.login(EMAIL_USER, constants.GMAIL_APP_PASSWORD)

        email_logger.info("sending...")
        server.sendmail(EMAIL_USER, to, message)

        server.close()

        email_logger.info("done")

    async def verify_email(self, ctx: Context, email: str):
        author_id = ctx.author.id

        if not (EMAIL_REGEX.match(email)):
            logger.info(f"{author_id} tried to request code with non-ugent email")
            await ctx.reply(
                "This does not look like a valid UGent email address\nIf you think this is a mistake please contact a server admin"
            )

            return

        logger.info(f"verifying email '{email}' for {author_id}")

        verification_code = str(uuid.uuid4().int)

        conn = self.bot.pg_conn
        cursor = conn.cursor()
        cursor.execute(FIND_USER_QUERY.format(id=author_id))
        if (user := cursor.fetchone()) is not None:
            if user[2] is None:
                logger.info(
                    f"{author_id} requested verification for already verified user"
                )
                await ctx.reply(
                    "A verified user with this email address already exists"
                )
                return
            else:
                logger.info(f"{author_id} requested verification code reset")
                cursor.execute(
                    UPDATE_USER_QUERY.format(code=verification_code, id=author_id)
                )
                conn.commit()

                self.send_confirmation_email(email, verification_code)
                await ctx.reply(
                    f"It seems you had already requested a confirmation code before\nThis code has been revoked and a new one has been sent to '{email}'\nPlease use `$verify code <code>` now to complete verification"
                )

                return

        logger.info(f"{author_id} requested new verification code")
        cursor.execute(
            INSERT_USER_QUERY.format(id=author_id, email=email, code=verification_code)
        )
        conn.commit()

        self.send_confirmation_email(email, verification_code)
        await ctx.reply(
            f"A confirmation code has been sent to '{email}'\nPlease use `$verify code <code>` now to complete verification"
        )

    async def verify_code(self, ctx: Context, code: str):
        author_id = ctx.author.id

        logger.info(f"verifying code '{code}' for {author_id}")

        conn = self.bot.pg_conn
        cursor = conn.cursor()
        cursor.execute(FIND_USER_QUERY.format(id=author_id))
        user = cursor.fetchone()

        if user is None:
            logger.info(f"{author_id} attempted to verify without requesting a code")
            await ctx.reply(
                "It seems you are trying to verify a code without having requested one first\nPlease use `$verify email <email>` to request a code"
            )

            return

        if user[2] is None:
            logger.info(
                f"{author_id} attempted to verify again after already having been verified"
            )
            await ctx.reply(
                "It seems you are trying to verify again despite already having done so in the past\nIf you think this is a mistake please contact a server admin"
            )

            return

        stored_code: str = user[2]

        if code != stored_code:
            logger.info(f"{author_id} attempted to verify with an invalid code")
            await ctx.reply(
                "This verification code is incorrect\nIf you would like to request a new code you may do so by using `$verify email <email>`"
            )

            return

        cursor.execute(VERIFY_USER_QUERY.format(id=author_id))
        conn.commit()

        user = ctx.author

        logger.info(f"{author_id} verified succesfully")
        await user.add_roles(
            discord.utils.get(user.guild.roles, name=constants.VERIFIED_ROLE)
        )
        await ctx.reply(
            "You have verified succesfully! Welcome to the psychology server"
        )

    @command(name="verify")
    async def verify(self, ctx: Context, subcommand: Optional[str], arg: Optional[str]):
        if subcommand not in ["email", "code"]:
            await ctx.reply(
                "Please specify whether you are verifying your email or your confirmation code\neg. `$verify email freud@oedipus.com`\nor `$verify code 123456`"
            )

            return

        if arg is None:
            if subcommand == "email":
                await ctx.reply(
                    "Please also specify your email\neg. `$verify email freud@oedipus.com`"
                )
            else:
                await ctx.reply(
                    "Please also specify your confirmation code\neg. `$verify code 123456`"
                )

            return

        try:
            if subcommand == "email":
                await self.verify_email(ctx, arg)
            else:
                await self.verify_code(ctx, arg)
        except Exception as err:
            await ctx.reply("Something went wrong, please notify the server admins")
            logger.error(traceback.format_exc())


def setup(bot: Bot):
    bot.add_cog(Verify(bot))
