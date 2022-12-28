import importlib
import inspect
import pkgutil
from typing import Iterator, NoReturn

from discord import Interaction
from discord.app_commands import AppCommandError, errors
from discord.ext.commands import Context, CommandError, Cog

from bot import extensions
from bot.bot import Bot
from bot.events import Event
from bot.events.moderation import ModerationEvent
from bot.util import enable_guild_logging


class ErrorHandledCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def app_error_to_event(ia: Interaction, error: AppCommandError) -> Event:
        """Map an app command error and its interaction to a loggable event"""

        match error:
            case errors.MissingAnyRole:
                event = ModerationEvent.MissingRole(
                    ia.user, ia.command, error.missing_role
                )
            case errors.MissingPermissions:
                event = ModerationEvent.MissingPermissions(
                    ia.user, ia.command, error.missing_permissions
                )
            case _:
                raise NotImplementedError

        return event

    @staticmethod
    def error_to_event(ctx: Context, error: CommandError) -> Event:
        """Map a command error and its context to a loggable event"""

        match error:
            case errors.MissingAnyRole:
                event = ModerationEvent.MissingRole(
                    ctx.author, ctx.command, error.missing_role
                )
            case errors.MissingPermissions:
                event = ModerationEvent.MissingPermissions(
                    ctx.author, ctx.command, error.missing_permissions
                )
            case _:
                raise NotImplementedError

        return event

    @enable_guild_logging
    async def cog_app_command_error(self, ia: Interaction, error: AppCommandError):
        try:
            event = self.app_error_to_event(ia, error)
        except NotImplementedError:
            self.bot.logger.error(error)
            await ia.followup.send("Unknown error, please contact a server admin")
            return

        self.bot.logger.warning(event)
        await ia.response.send_message(event.human)

    @enable_guild_logging
    async def cog_command_error(self, ctx: Context, error: CommandError):
        try:
            event = self.app_error_to_event(ctx, error)
        except NotImplementedError:
            self.bot.logger.error(error)
            await ctx.reply("Unknown error, please contact a server admin")
            return

        self.bot.logger.warning(event)
        await ctx.response.send_message(event.human)


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
