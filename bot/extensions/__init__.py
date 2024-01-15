import importlib
import inspect
import pkgutil
import traceback
from typing import Iterator, NoReturn

from discord import Interaction
from discord import errors as discord_errors
from discord import HTTPException as http_errors
from discord.app_commands import AppCommandError, errors as app_errors
from discord.ext.commands import Context, CommandError, Cog, errors as cmd_errors

from bot import extensions, root_logger, exceptions as bot_errors
from bot.bot import Bot
from bot.events import Event
from bot.events.config import ConfigEvent
from bot.events.moderation import ModerationEvent


logger = root_logger.getChild("bot")


class ErrorHandledCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def app_error_to_event(ia: Interaction, error: AppCommandError) -> Event:
        """Map an app command error and its interaction to a loggable event"""

        match type(error):
            case app_errors.CommandInvokeError:
                original = error.original

                match type(original):
                    case discord_errors.Forbidden:
                        forbidden_error: discord_errors.Forbidden = original

                        match forbidden_error.code:
                            case 50007:
                                event = Event.cannot_message_user(ia.user, ia.command)
                            case _:
                                event = Event.forbidden(ia.user, ia.command)
                    case _:
                        event = Event.unknown_error()
            case app_errors.MissingRole:
                event = ModerationEvent.missing_role(
                    ia.user, ia.command, error.missing_role
                )
            case app_errors.MissingPermissions:
                event = ModerationEvent.missing_permissions(
                    ia.user, ia.command, error.missing_permissions
                )
            case bot_errors.MissingConfig:
                event = ConfigEvent.missing_config(ia.guild)
            case bot_errors.MissingConfigOption:
                event = ConfigEvent.missing_config_option(ia.guild, error.option)
            case bot_errors.WrongChannel:
                event = ModerationEvent.wrong_channel(
                    error.user, error.cmd, error.used_channel, error.allowed_channel
                )
            case _:
                event = Event.unknown_error()

        return event

    @staticmethod
    def error_to_event(ctx: Context, error: CommandError) -> Event:
        """Map a command error and its context to a loggable event"""

        match type(error):
            case cmd_errors.MissingPermissions:
                event = ModerationEvent.missing_permissions(
                    ctx.author, ctx.command, error.missing_permissions
                )
            case _:
                event = Event.unknown_error()

        return event

    async def cog_app_command_error(self, ia: Interaction, error: AppCommandError):
        event = self.app_error_to_event(ia, error)

        if event.error:
            logger.error(traceback.format_exc())
            self.bot.logger.error(event)
            self.bot.discord_logger.error(event, guild=ia.guild)
        else:
            self.bot.discord_logger.warning(event, guild=ia.guild)

        await ia.followup.send(content=event.user_msg, ephemeral=True)

    async def cog_command_error(self, ctx: Context, error: CommandError):
        event = self.app_error_to_event(ctx, error)

        self.bot.discord_logger.warning(event, guild=ctx.guild)
        await ctx.reply(event.user_msg, ephemeral=True)


def walk_extensions() -> Iterator[str]:
    """Yield all extension names from the bot.extensions package"""

    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)

    for module in pkgutil.walk_packages(
        extensions.__path__, f"{extensions.__name__}.", onerror=on_error
    ):
        if module.ispkg:
            imported = importlib.import_module(module.name)
            if not inspect.isfunction(getattr(imported, "setup", None)):
                # Skip extensions without a setup function
                continue

        yield module.name


EXTENSIONS = frozenset(walk_extensions())
