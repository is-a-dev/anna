from __future__ import annotations

import nextcord
from nextcord.ext import commands


class DeleteResponse(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: nextcord.RawReactionActionEvent) -> None:
        if event.event_type == "REACTION_ADD":
            # print(event.emoji == "<:delete:1236642973576331328>")
            if str(event.emoji) == "<:delete:1236642973576331328>":
                # Do not delete suggestions
                if event.channel_id == 1236200920317169695:
                    return
                n = await self._bot.get_channel(event.channel_id).fetch_message(
                    event.message_id
                )
                if not self._bot.get_user(event.user_id).bot:  # type: ignore[reportOptionalMemberAccess]
                    if n.author.id == self._bot.user.id:  # type: ignore[reportOptionalMemberAccess]
                        await n.delete()
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DeleteResponse(bot))
