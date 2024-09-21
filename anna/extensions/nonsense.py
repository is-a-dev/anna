# Copyright (c) 2024 - present, MaskDuck

## code has been modified and is not the original code from MaskDuck

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional, cast

import aiohttp
import nextcord
from nextcord import (
    HTTPException,
    Interaction,
    Object,
    SlashOption,
    TextChannel,
    slash_command,
)
from nextcord.ext import application_checks as ac
from nextcord.ext import commands

from .converters import (
    EnsureHTTPConverter,
    SlashEnsureHTTPConverter,
    SlashSubdomainNameConverter,
    SubdomainNameConverter,
)
from .types import Domain


class DomainNotExistError(commands.CommandError):
    """Error raised when domain cannot be found."""


class LinkView(nextcord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(
            nextcord.ui.Button(label="Main Website", url="https://is-a.dev", row=1)
        )
        self.add_item(
            nextcord.ui.Button(
                label="Documentation", url="https://is-a.dev/docs", row=1
            )
        )
        self.add_item(
            nextcord.ui.Button(
                label="Register a domain!",
                url="https://github.com/is-a-dev/register",
                row=1,
            )
        )
        self.add_item(
            nextcord.ui.Button(label="GitHub", url="https://github.com/is-a-dev", row=1)
        )
        # self.add_item(nextcord.ui.Button(label="Help Channel", url="", row=4))


async def request(requesting_domain: bool = False, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            if ans.status == 404 and requesting_domain:
                raise DomainNotExistError("imagine")
            return await ans.json(content_type=None)


request.__doc__ = aiohttp.ClientSession.request.__doc__


class Nonsense(commands.Cog):
    """Various utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    async def links(self, ctx: commands.Context):
        """Links to the is-a.dev documentation, FAQ, etc."""
        embed = nextcord.Embed(
            title="Links that are important to this service.",
            description="Please also check those channels:\n- <#991779321758896258> (for an interactive experience type `a?faq`)\n- <#1228996111390343229>",
            color=nextcord.Color.blue(),
        )
        await ctx.send(embed=embed, view=LinkView())

    @commands.command()
    async def regex(self, ctx: commands.Context, pattern: str, string: str):
        r: Optional[re.Match] = re.fullmatch(pattern, string)
        if r:
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")

    @commands.command()
    async def screenshot(self, ctx: commands.Context, url: EnsureHTTPConverter):
        """Screenshots a webpage. Usage: `a?screenshot https://example.com`."""
        await ctx.send(
            embed=nextcord.Embed(
                title="Screenshot",
                description=f"[Open in browser for fast rendering](http://image.thum.io/get/{url})",
                color=nextcord.Color.blue(),
            )
        )

    @classmethod
    def fetch_description_about_a_domain(cls, data: Domain):
        parsed_contact = {}
        for platform, username in data["owner"].items():
            if platform == "username":
                parsed_contact["github"] = (
                    f"[{username}](https://github.com/{username})"
                )
            elif platform == "twitter":
                parsed_contact["twitter"] = (
                    f"[{username}](https://twitter.com/{username})"
                )
            elif platform == "email":
                if username != "":
                    parsed_contact["email"] = username
            else:
                # unknown contact, ignoring
                parsed_contact[platform] = username

        contact_desc = """**Contact Info**:\n"""
        for x, y in parsed_contact.items():
            contact_desc += f"**{x}**: {y}\n"

        record_desc = """**Record Info**:\n"""
        for x, y in data["record"].items():
            if x == "CNAME":
                record_desc += f"**{x}**: [{y}](https://{y})\n"
            else:
                record_desc += f"**{x}**: {y}\n"

        if domain_desc := data.get("description"):
            domain_desc = "**Description**: " + domain_desc + "\n"
        else:
            domain_desc = None

        if repo := data.get("repo"):
            repo_desc = "**Repository**: " + f"[here]({repo})" + "\n"
        else:
            repo_desc = None

        # do not ask about the description of this thing
        my_description = f"""
        {contact_desc}

        {record_desc}
        """
        if domain_desc is not None:
            my_description += domain_desc + "\n"
        if repo_desc is not None:
            my_description += repo_desc + "\n"
        return my_description

    @commands.command()
    async def whois(
        self, ctx: commands.Context, domain: SubdomainNameConverter
    ) -> None:
        """Lookup information about an is-a.dev domain."""
        k = nextcord.ui.View()
        k.add_item(
            nextcord.ui.Button(
                style=nextcord.ButtonStyle.url,
                url=f"https://github.com/is-a-dev/register/edit/main/domains/{domain}.json",
                label="Edit this subdomain?",
            )
        )
        try:
            data = await request(
                True,
                "GET",
                f"https://raw.githubusercontent.com/is-a-dev/register/main/domains/{domain}.json",
            )
        except DomainNotExistError:
            await ctx.send("The domain queried cannot be found. Aborting.")
            return
        embed = nextcord.Embed(
            color=nextcord.Color.blue(),
            title=f"Info about {domain}.is-a.dev",
            description=self.fetch_description_about_a_domain(data),
        )
        await ctx.send(embed=embed, view=k)

    @commands.command()
    async def check(
        self, ctx: commands.Context, domain: SubdomainNameConverter
    ) -> None:
        """Checks if an is-a.dev domain is available."""
        try:
            await request(
                True,
                "GET",
                f"https://raw.githubusercontent.com/is-a-dev/register/main/domains/{domain}.json",
            )
            embed = nextcord.Embed(
                color=nextcord.Color.blue(),
                description=f"Sorry, [{domain}.is-a.dev](<https://{domain}.is-a.dev>) is taken.",
            )
            await ctx.send(embed=embed)
        except DomainNotExistError:
            embed = nextcord.Embed(
                color=nextcord.Color.blue(),
                description=f"Congratulations, [{domain}.is-a.dev](<https://{domain}.is-a.dev>) is available!",
            )
            await ctx.send(embed=embed)


class NonsenseSlash(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @nextcord.slash_command()
    async def ban(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = SlashOption(
            description="The member to ban", required=True
        ),
        reason: str = SlashOption(description="The reason to ban", required=True),
    ) -> None:
        """A fake ban command."""
        await interaction.send(f"Banned <@{user.id}> for **{reason}**")

    @nextcord.slash_command()
    async def check(
        self,
        interaction: nextcord.Interaction,
        domain: SlashSubdomainNameConverter = SlashOption(
            description="The domain name to check for.", required=True
        ),
    ) -> None:
        try:
            await request(
                True,
                "GET",
                f"https://raw.githubusercontent.com/is-a-dev/register/main/domains/{domain}.json",
            )
            embed = nextcord.Embed(
                color=nextcord.Color.blue(),
                description=f"Sorry, [{domain}.is-a.dev](<https://{domain}.is-a.dev>) is taken.",
            )
            await interaction.send(embed=embed)
        except DomainNotExistError:
            embed = nextcord.Embed(
                color=nextcord.Color.blue(),
                description=f"Congratulations, [{domain}.is-a.dev](<https://{domain}.is-a.dev>) is available!",
            )
            await interaction.send(embed=embed)

    @slash_command()
    async def whois(
        self,
        interaction: Interaction,
        domain: SlashSubdomainNameConverter = SlashOption(
            description="The is-a.dev domain name to lookup information for.",
            required=True,
        ),
    ) -> None:
        try:
            data = await request(
                True,
                "GET",
                f"https://raw.githubusercontent.com/is-a-dev/register/main/domains/{domain}.json",
            )
            view = nextcord.ui.View()

            view.add_item(
                nextcord.ui.Button(
                    style=nextcord.ButtonStyle.url,
                    url=f"https://github.com/is-a-dev/register/edit/main/domains/{domain}.json",
                    label="Edit this subdomain?",
                )
            )
            await interaction.send(
                embed=nextcord.Embed(
                    title=f"Domain info for {domain}.is-a.dev",
                    description=Nonsense.fetch_description_about_a_domain(data),
                    color=nextcord.Color.blue(),
                ),
                view=view,
            )
        except DomainNotExistError:
            await interaction.send("Domain requested cannot be found. Aborting.")

    @slash_command()
    async def links(self, interaction: Interaction) -> None:
        embed = nextcord.Embed(
            title="Links that are important to this service.",
            description="Please also check those channels:\n- <#991779321758896258> (for an interactive experience type `a?faq`)\n- <#1228996111390343229>",
            color=nextcord.Color.blue(),
        )
        await interaction.send(embed=embed, view=LinkView())

    @slash_command()
    async def screenshot(self, interaction: Interaction) -> None:
        pass

    @screenshot.subcommand()
    async def from_url(
        self,
        interaction: Interaction,
        url: SlashEnsureHTTPConverter = SlashOption(
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
    bot.add_cog(Nonsense(bot))
    bot.add_cog(NonsenseSlash(bot))
