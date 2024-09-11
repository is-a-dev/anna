#Copyright (c) 2024 - present, MaskDuck

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from nextcord import AllowedMentions, Object
from nextcord.ext import commands

if TYPE_CHECKING:
    from nextcord import Message

CUTEDOG_ALT_ID: Final[int] = 740117772566265876


class PingCutedog(commands.Cog):
    @commands.Cog.listener("on_message")
    async def ping_cutedog(self, message: Message) -> None:
        if CUTEDOG_ALT_ID in [x.id for x in message.mentions]:
            await message.channel.send(
                "<@716306888492318790>",
                allowed_mentions=AllowedMentions(users=[Object(id=716306888492318790)]),
            )


def setup(bot: commands.Bot):
    bot.add_cog(PingCutedog())
