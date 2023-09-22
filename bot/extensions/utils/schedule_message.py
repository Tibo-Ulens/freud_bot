import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional

from discord import app_commands, Interaction, TextChannel, TextStyle
from discord.ui import Modal, TextInput

from bot.bot import Bot
from bot.decorators import check_user_has_admin_role
from bot.extensions import ErrorHandledCog


class ExpiredTimestamp(ValueError):
    """Timestamp was in the past"""

    def __init__(self, timestamp: str, delay: timedelta):
        self.info = f"Error: message would have been sent in the past ({timestamp}, {delay} ago)"

        super().__init__()


def schedule_message(
    loop, channel: TextChannel, parsed_time: str, message: str
) -> timedelta:
    now: datetime = datetime.now().astimezone(timezone.utc).replace(microsecond=0)
    parsed_with_tz: datetime = parsed_time.astimezone(timezone.utc).replace(
        microsecond=0
    )

    delay: timedelta = parsed_with_tz - now

    if delay.total_seconds() < 0:
        raise ExpiredTimestamp(parsed_time, -delay)

    async def _schedule_message(channel: TextChannel, delay: float, message: str):
        await asyncio.sleep(delay)
        await channel.send(content=message)

    loop.create_task(_schedule_message(channel, delay.total_seconds(), message))

    return delay


class MessagePrompt(Modal):
    message = TextInput(label="message", style=TextStyle.paragraph)

    def __init__(
        self,
        loop,
        channel: TextChannel,
        parsed_time: str,
    ) -> None:
        self.loop = loop
        self.channel = channel
        self.parsed_time = parsed_time

        super().__init__(title="Message", timeout=None)

    async def on_submit(self, ia: Interaction):
        message = self.message.value

        try:
            delay = schedule_message(self.loop, self.channel, self.parsed_time, message)
        except ExpiredTimestamp as err:
            return await ia.response.send_message(err.info)

        return await ia.response.send_message(
            f"Message scheduled to be sent in {delay}, at {self.parsed_time}"
        )


class ScheduleMessage(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.loop = asyncio.get_event_loop()

        super().__init__(bot)

    @app_commands.command(
        name="schedule", description="Schedule a message to be sent at a specific time"
    )
    @app_commands.guild_only()
    @check_user_has_admin_role()
    @app_commands.describe(
        channel="The channel to post the message in",
        time="The time to post the message at (format %Y/%m/%d %H:%M)",
        tz="The timezone of your timestamp, default UTC (UTC = 0000, CET = 0100, CEST = 0200)",
        message="The message to post, if not provided a popup window will be opened to type a message",
    )
    @app_commands.rename(tz="timezone")
    async def schedule_message(
        self,
        ia: Interaction,
        channel: TextChannel,
        time: str,
        tz: Optional[str] = "0000",
        message: Optional[str] = None,
    ):
        try:
            parsed_time = datetime.strptime(time + f"+{tz}", "%Y/%m/%d %H:%M%z")
        except ValueError:
            return await ia.response.send_message(
                f"Invalid timestamp, it should be in the format `%Y/%m/%d %H:%M`, found {time}",
                ephemeral=True,
            )

        if message is None:
            return await ia.response.send_modal(
                MessagePrompt(self.loop, channel, parsed_time)
            )

        try:
            delay = schedule_message(self.loop, channel, parsed_time, message)
        except ExpiredTimestamp as err:
            return await ia.response.send_message(err.info)

        return await ia.response.send_message(
            f"Message scheduled to be sent in {delay}, at {parsed_time}"
        )


async def setup(bot: Bot):
    await bot.add_cog(ScheduleMessage(bot))
