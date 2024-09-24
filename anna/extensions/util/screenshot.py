# Copyright (c) 2024 - present, MaskDuck

import nextcord
from nextcord.ext import commands
from extensions.libs.converters import EnsureHTTPConverter, SlashEnsureHTTPConverter 

class Screenshot(commands.Cog):
    """Various utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    async def screenshot(self, ctx: commands.Context, url: EnsureHTTPConverter):
        """Screenshots a webpage. Usage: `a?screenshot https://example.com`."""
        await ctx.reply(
            embed=nextcord.Embed(
                title="Screenshot",
                description=f"[Open in browser for fast rendering](http://image.thum.io/get/{url})",
                color=nextcord.Color.blue(),
            )
        , mention_author=False)

    @nextcord.slash_command(name=screenshot)
    async def screenshot_slash(
        self,
        interaction: nextcord.Interaction,
        url: SlashEnsureHTTPConverter = nextcord.SlashOption(
            description="The URL to screenshot", required=True
        ),
    ) -> None:
        """Screenshot an URL."""
        await interaction.send(
            embed=nextcord.Embed(
                title="Screenshot",
                description=f"[Open in browser for fast rendering](https://image.thum.io/get/{url})",
                color=nextcord.Color.blue(),
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(Screenshot(bot))
