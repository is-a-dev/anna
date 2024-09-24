# Copyright (c) 2024 - present, MaskDuck

# code has been modified and is not the original code from MaskDuck

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional, cast

import aiohttp
import nextcord
from nextcord.ext import application_checks as ac
from nextcord.ext import commands

from extensions.libs.converters import SlashSubdomainNameConverter, SubdomainNameConverter
from extensions.libs.types import Domain


class DomainNotExistError(commands.CommandError):
    """Error raised when domain cannot be found."""

async def request(requesting_domain: bool = False, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            if ans.status == 404 and requesting_domain:
                raise DomainNotExistError("imagine")
            return await ans.json(content_type=None)


request.__doc__ = aiohttp.ClientSession.request.__doc__


class SubdomainUtils(commands.Cog):
    """Various utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
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
        """Lookup information about an is-a.dev domain. Usage: `a?whois domain.is-a.dev`."""
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
            await ctx.reply("The domain queried cannot be found. Aborting.", mention_author=False)
            return
        embed = nextcord.Embed(
            color=nextcord.Color.blue(),
            title=f"Info about {domain}.is-a.dev",
            description=self.fetch_description_about_a_domain(data),
        )
        await ctx.reply(embed=embed, view=k, mention_author=False)

    @commands.command()
    async def check(
        self, ctx: commands.Context, domain: SubdomainNameConverter
    ) -> None:
        """Checks if an is-a.dev domain is available. Usage: `a?check domain.is-a.dev`."""
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
            await ctx.reply(embed=embed, mention_author=False)
        except DomainNotExistError:
            embed = nextcord.Embed(
                color=nextcord.Color.blue(),
                description=f"Congratulations, [{domain}.is-a.dev](<https://{domain}.is-a.dev>) is available!",
            )
            await ctx.reply(embed=embed, mention_author=False)


class SubdomainUtilsSlash(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @nextcord.slash_command(name="slash")
    async def check(
        self,
        interaction: nextcord.Interaction,
        domain: SlashSubdomainNameConverter = nextcord.SlashOption(
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

    @nextcord.slash_command(name="whois")
    async def whois_slash(
        self,
        interaction: nextcord.Interaction,
        domain: SlashSubdomainNameConverter = nextcord.SlashOption(
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
                    description=SubdomainUtils.fetch_description_about_a_domain(data),
                    color=nextcord.Color.blue(),
                ),
                view=view,
            )
        except DomainNotExistError:
            await interaction.send("Domain requested cannot be found. Aborting.")

def setup(bot: commands.Bot):
    bot.add_cog(SubdomainUtils(bot))
    bot.add_cog(SubdomainUtilsSlash(bot))
