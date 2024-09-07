from __future__ import annotations

from typing import Generic, TypeVar

import aiohttp
import nextcord
from nextcord.ext import commands, menus

T = TypeVar("T")


class NixWikiPageSource(menus.ListPageSource, Generic[T]):
    async def format_page(self, menu: menus.Menu, page: T) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=page[0],
            description=page[1],
            color=nextcord.Color.from_rgb(23, 147, 209),
        )
        embed.set_image(
            url="https://perfectmediaserver.com/images/logos/nixos-logo.png"
        )
        return embed

    async def get_page(self, page_number: int) -> T:
        k = self.entries
        return [k[1][page_number], k[3][page_number]]

    def get_max_pages(self):
        return len(self.entries[1])


class NixWikiButtonMenu(menus.ButtonMenuPages):
    def __init__(self, query_result):
        super().__init__(
            NixWikiPageSource(query_result, per_page=1), nextcord.ButtonStyle.green
        )


class NixWiki(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.command()
    async def nixwiki(self, ctx: commands.Context, *, query: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://nixos.wiki/api.php?action=opensearch&search={query}&limit=20&format=json"
            ) as resp:
                k = await resp.json()
                if len(k[1]) == 0:
                    await ctx.send("No results found")
                    return
                l: NixWikiButtonMenu = NixWikiButtonMenu(k)
                await l.start(ctx=ctx)

    @nextcord.slash_command(name="nixwiki")
    async def nixwiki_(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(
            description="The query of the documentation page to search for.",
            required=True,
        ),
    ) -> None:
        """Query the NixWiki Documentation for a specified query."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://nixos.wiki/api.php?action=opensearch&search={query}&limit=20&format=json"
            ) as resp:
                k = await resp.json()
                if len(k[1]) == 0:
                    await interaction.send("No results found")
                    return
                l: NixWikiButtonMenu = NixWikiButtonMenu(k)
                await l.start(interaction=interaction)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(NixWiki(bot))
