from __future__ import annotations

from typing import Final, Generic, Self, TypeVar

import aiohttp
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands, menus

T = TypeVar("T")

ARCHLINUX_IMAGE_URL: Final[str] = (
    "https://archlinux.org/static/logos/archlinux-logo-dark-1200dpi.b42bd35d5916.png"
)


class ArchWikiPageSource(menus.ListPageSource, Generic[T]):
    async def format_page(self, menu: menus.Menu, page: T) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=page[0],
            description=page[1],
            color=nextcord.Color.from_rgb(23, 147, 209),
        )
        embed.set_image(url=ARCHLINUX_IMAGE_URL)
        return embed

    async def get_page(self, page_number: int) -> T:
        k = self.entries
        return [k[1][page_number], k[3][page_number]]

    def get_max_pages(self):
        return len(self.entries[1])


class ArchWikiButtonMenu(menus.ButtonMenuPages):
    def __init__(self, query_result):
        super().__init__(
            ArchWikiPageSource(query_result, per_page=1), nextcord.ButtonStyle.blurple
        )


class ArchWiki(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.command()
    async def archwiki(self, ctx: commands.Context, *, query: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://wiki.archlinux.org/api.php?action=opensearch&search={query}&limit=20&format=json"
            ) as resp:
                k = await resp.json()
                if len(k[1]) == 0:
                    await ctx.send("No results found")
                    return
                l: ArchWikiButtonMenu = ArchWikiButtonMenu(k)
                await l.start(ctx=ctx)

    @nextcord.slash_command(name="archwiki")
    async def archwiki_(
        self: Self,
        interaction: nextcord.Interaction,
        query: str = SlashOption(
            description="The documentation query to search for", required=True
        ),
    ):
        """Query ArchWiki for a documentation entry."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://wiki.archlinux.org/api.php?action=opensearch&search={query}&limit=20&format=json"
            ) as resp:
                k = await resp.json()
                if len(k[1]) == 0:
                    await interaction.send("No results found, aborting.")
                    return
                l: ArchWikiButtonMenu = ArchWikiButtonMenu(k)
                await l.start(interaction=interaction)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ArchWiki(bot))
