import logging

import discord
from discord import app_commands, Interaction
from discord.ext.commands import Cog
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

from bot.bot import Bot


class Calendar(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="calendar",
        description="Show your personal calendar for this week, or add/remove courses",
    )
    async def calendar(self, iactn: Interaction):
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get("https://wiki.archlinux.org/")

        await iactn.response.send_message("done")


async def setup(bot: Bot):
    await bot.add_cog(Calendar(bot))
