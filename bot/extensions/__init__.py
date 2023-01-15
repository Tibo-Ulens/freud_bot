import importlib
import inspect
import pkgutil
import traceback
from typing import Iterator, NoReturn

from discord import Interaction
from discord.app_commands import AppCommandError, errors as app_errors
from discord.ext.commands import Context, CommandError, Cog, errors as cmd_errors

from bot import extensions, root_logger, exceptions as bot_errors
from bot.bot import Bot
from bot.decorators import store_command_context
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

    @store_command_context
    async def cog_app_command_error(self, ia: Interaction, error: AppCommandError):
        event = self.app_error_to_event(ia, error)

        if event.error:
            logger.error(traceback.format_exc())
            self.bot.logger.error(event)
        else:
            self.bot.logger.warning(event)

        await ia.response.send_message(event.user_msg)

    @store_command_context
    async def cog_command_error(self, ctx: Context, error: CommandError):
        event = self.app_error_to_event(ctx, error)

        self.bot.logger.warning(event)
        await ctx.response.send_message(event.user_msg)


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
