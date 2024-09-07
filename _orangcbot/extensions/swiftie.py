from __future__ import annotations

import nextcord
from nextcord.ext import commands


class Swiftie(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message) -> None:
        if message.author.id == 850820069310201896 and "'" in message.content:
            await message.reply("swiftie detected.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Swiftie(bot))
