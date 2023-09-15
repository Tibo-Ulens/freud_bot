import logging
import re
import smtplib
import uuid

import discord
from discord import app_commands, Interaction, Member, Locale, ButtonStyle
from discord.ui import View, Button, Modal, TextInput

from models.profile import Profile
from models.config import Config

from bot import constants, util
from bot.bot import Bot
from bot.decorators import (
    store_command_context,
    check_has_config_option,
    only_in_channel,
)
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


class VerifyEmailModal(Modal, title=""):
    email = TextInput(label="email", placeholder="jan.peeters@ugent.be")

    async def on_submit(self, ia: Interaction):
        email = self.email.value
        author_id = ia.user.id
        verification_code = str(uuid.uuid4().hex)

        profile = await Profile.find_by_discord_id(author_id)
        if profile is not None:
            if profile.confirmation_code is None:
                # self.bot.discord_logger.warning(
                #     f"user {util.render_user(ia.user)} attempted to verify despite already being verified"
                # )
                await ia.response.send_message(
                    "It seems you are trying to verify again despite already having done so in the past\nIf you think this is a mistake please contact a server admin",
                    ephemeral=True,
                )
                return
            else:
                profile.confirmation_code = verification_code
                # Users might have mistyped their email, update it just in case
                profile.email = email
                await profile.save()

                send_confirmation_email(email, verification_code)

                verify_code_view = View(timeout=None)
                verify_code_view.add_item(
                    VerifyCodeButton(style=ButtonStyle.green, label="verify code")
                )

                await ia.response.send_message(
                    f"It seems you had already requested a confirmation code before\nThis code has been revoked and a new one has been sent to '{email}'",
                    view=verify_code_view,
                    ephemeral=True,
                )

                return

        other = await Profile.find_by_email(email)
        if other is not None:
            # self.bot.discord_logger.warning(
            #     f"user {util.render_user(ia.user)} attempted to verify with duplicate email {email}"
            # )
            await ia.response.send_message(
                "A different profile with this email already exists\nIf you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        # self.bot.logger.info(
        #     f"user {util.render_user(ia.user)} requested verification code for {email}"
        # )
        await Profile.create(
            discord_id=author_id, email=email, confirmation_code=verification_code
        )

        send_confirmation_email(email, verification_code)

        verify_code_view = View(timeout=None)
        verify_code_view.add_item(
            VerifyCodeButton(style=ButtonStyle.green, label="verify code")
        )

        await ia.response.send_message(
            content=f"A confirmation code has been sent to '{email}'",
            view=verify_code_view,
        )


class VerifyCodeModal(Modal, title=""):
    code = TextInput(label="code", placeholder="1234567890")

    async def on_submit(self, ia: Interaction):
        code = self.code.value
        author_id = ia.user.id
        profile = await Profile.find_by_discord_id(author_id)

        if profile is None:
            # self.bot.discord_logger.warning(
            #     f"user {util.render_user(ia.user)} attempted to verify without requesting a code"
            # )
            await ia.response.send_message(
                "It seems you are trying to verify a code without having requested one first\nPlease use `/verify <email>` to request a code",
                ephemeral=True,
            )

            return

        if profile.confirmation_code is None:
            # self.bot.discord_logger.warning(
            #     f"user {util.render_user(ia.user)} attempted to verify despite already being verified"
            # )
            await ia.response.send_message(
                "It seems you are trying to verify again despite already having done so in the past\nIf you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        stored_code: str = profile.confirmation_code

        if code != stored_code:
            # self.bot.discord_logger.warning(
            #     f"user {util.render_user(ia.user)} attempted to verify with an invalid code"
            # )
            await ia.response.send_message(
                "This verification code is incorrect\nIf you would like to request a new code you may do so by using `/verify <email>`",
                ephemeral=True,
            )
            return

        # user = ia.user

        # config = await Config.get(ia.guild_id)
        # verified_role = config.verified_role

        # await user.add_roles(discord.utils.get(user.guild.roles, id=verified_role))

        profile.confirmation_code = None
        await profile.save()

        # self.bot.logger.info(f"user {util.render_user(ia.user)} verified succesfully")
        await ia.response.send_message(
            "You have verified succesfully! Welcome to the server"
        )


class VerifyEmailButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def callback(self, ia: Interaction):
        await ia.response.send_modal(VerifyEmailModal())


class VerifyCodeButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def callback(self, ia: Interaction):
        await ia.response.send_modal(VerifyCodeModal())


class Verification(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="verify", description="Verify that you are a true UGentStudent"
    )
    @app_commands.describe(argument="Your UGent email or verification code")
    @only_in_channel("verification_channel")
    @check_has_config_option("verification_channel")
    @check_has_config_option("verified_role")
    @store_command_context
    async def verify(self, ia: Interaction, argument: str):
        verify_email_view = View(timeout=None)
        verify_email_view.add_item(
            VerifyEmailButton(style=ButtonStyle.green, label="verify")
        )

        await ia.response.send_message(content="verifying", view=verify_email_view)
        # msg = argument.strip().lower()

        # if len(msg.split(" ")) != 1:
        #     await ia.response.send_message(
        #         "This command only takes one argument\neg. `/verify freud@oedipus.com`\nor `/verify 123456`",
        #         ephemeral=True,
        #     )

        #     return

        # if EMAIL_REGEX.match(msg):
        #     await self.verify_email(ia, msg)
        # elif match := CODE_REGEX.search(msg):
        #     code = match.group(1)
        #     await self.verify_code(ia, code)
        # else:
        #     self.bot.discord_logger.warning(
        #         f"user {util.render_user(ia.user)} attempted to verify with malformed argument '{msg}'"
        #     )
        #     await ia.response.send_message(
        #         "This doesn't look like a valid UGent email or a valid verification code\nIf you think this is a mistake please contact a server admin",
        #         ephemeral=True,
        #     )

    @ErrorHandledCog.listener("on_member_join")
    async def handle_member_join(self, member: Member):
        guild = member.guild

        # Exit if there's no verified role configured yet
        guild_config = await Config.get(guild.id)
        if guild_config is None or guild_config.verified_role is None:
            return

        # Ensure the profile exists
        profile = await Profile.find_by_discord_id(member.id)
        if profile is None:
            return

        # If the profile is already verified somehwere else, verify them here
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
        verify_email_view.add_item()

        dm_channel.send(
            content=guild_config.verify_email_message,
        )


async def setup(bot: Bot):
    await bot.add_cog(Verification(bot))
