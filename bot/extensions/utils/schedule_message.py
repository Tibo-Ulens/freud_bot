import asyncio
from datetime import datetime
from typing import Optional

from discord import app_commands, Interaction, TextChannel

from bot.bot import Bot
from bot.extensions import ErrorHandledCog


class ScheduleMessage(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.loop = asyncio.get_event_loop()

        super().__init__(bot)

    async def send_delayed_message(
        self, channel: TextChannel, timestamp: datetime, message: str
    ):
        now = datetime.now()
        delay = (timestamp - now).total_seconds()

        self.bot.logger.info(f"message scheduled in {timestamp} - {now} = {delay}s")

        await asyncio.sleep((timestamp - now).total_seconds())

        await channel.send(content=message)

    @app_commands.command(
        name="schedule", description="schedule a message to be sent at a specific time"
    )
    @app_commands.describe(
        time="the time to post the message at",
        message="the message to post",
    )
    async def schedule_message(
        self,
        ia: Interaction,
        channel: TextChannel,
        time: str,
        message: Optional[str] = None,
    ):
        try:
            parsed = datetime.strptime(time, "%Y/%m/%d %H:%M")
        except ValueError:
            return await ia.response.send_message(
                f"Invalid timestamp, it should be in the format `%Y/%m/%d %H:%M`, found {time}",
                ephemeral=True,
            )

        self.loop.create_task(self.send_delayed_message(channel, parsed, message))

        return await ia.response.send_message(f"message scheduled for {parsed}")


async def setup(bot: Bot):
    await bot.add_cog(ScheduleMessage(bot))
