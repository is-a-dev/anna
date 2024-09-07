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
                label="Documentation", url="https://is-a.dev/docs", row=2
            )
        )
        self.add_item(
            nextcord.ui.Button(
                label="Register a domain!",
                url="https://github.com/is-a-dev/register",
                row=3,
            )
        )
        # self.add_item(nextcord.ui.Button(label="Help Channel", url="", row=4))


async def request(requesting_domain: bool = False, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            if ans.status == 404 and requesting_domain:
                raise DomainNotExistError("imagine")
            return await ans.json(content_type=None)


request.__doc__ = aiohttp.ClientSession.request.__doc__


class ReportDegenModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Degenerate Report")
        self.degen = nextcord.ui.TextInput(
            "Name of suspected degenerate", required=True
        )
        self.reason = nextcord.ui.TextInput(
            "Why they're a degenerate",
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.degen)
        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user.id == 716134528409665586:
            await interaction.send(
                f"Thank you for informing me, Master. I'm sorry for my incompetence and I will deal with **{self.degen.value}** in no time. Sorry to let you down, Master."
            )
        elif interaction.user.id == 961063229168164864:
            await interaction.send("Isn't you and him one and the same?")
        else:
            await interaction.send(
                f"Actually, you would be a better degenerate than **{self.degen.value}**. Invalid report."
            )


class ProposeView(nextcord.ui.View):
    if TYPE_CHECKING:
        message: nextcord.Message | nextcord.InteractionMessage

    def __init__(self, spouse_id: int):
        super().__init__(timeout=30)
        self._spouse_id: int = spouse_id
        self._answered: Optional[bool] = None

    def update_msg(self, msg: nextcord.Message | nextcord.InteractionMessage):
        self._message = msg

    @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.green)
    async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        for child in self.children:
            child.disabled = True
        self._answered = True
        await interaction.response.defer()
        await self._message.edit("I love you!", view=self)

    @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.red)
    async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        for child in self.children:
            child.disabled = True
        self._answered = True
        await interaction.response.defer()
        await self._message.edit("I hereby refuse your refusal.", view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True  # type: ignore
        if not self._answered:
            await self._message.edit("You missed the boat. Failure.", view=self)  # type: ignore

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id == self._spouse_id:
            return True
        else:
            await interaction.send("Fool", ephemeral=True)
            return False


class ReportDegenView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.message: nextcord.Message | None = None

    def update_msg(self, msg: nextcord.Message):
        self.message: nextcord.Message | None = msg

    @nextcord.ui.button(label="Report a Degenerate")
    async def report_degen(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction  # type: ignore[reportUnusedVariable]
    ) -> None:
        if interaction.user.id == self.message.author.id:
            await interaction.response.send_modal(ReportDegenModal())
        else:
            await interaction.send("Fool", ephemeral=True)


class Nonsense(commands.Cog):
    """Features that exists for no reason.
    Don't ask why."""

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    async def links(self, ctx: commands.Context):
        """Links that are important to this service."""
        k = """Please also check those channels:
        <#991779321758896258> (for an interactive experience go to <#960446827579199488> and type `oc/faq`)
        <#1228996111390343229>
        """
        await ctx.send(k, view=LinkView())

    @commands.command()
    async def regex(self, ctx: commands.Context, pattern: str, string: str):
        r: Optional[re.Match] = re.fullmatch(pattern, string)
        if r:
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")

    @commands.command()
    async def report_degenerate(self, ctx: commands.Context):
        k = ReportDegenView()
        await ctx.send("Found a degen? Report them here.", view=k)
        k.update_msg(ctx.message)

    @commands.command()
    async def propose(self, ctx: commands.Context):
        k = ProposeView(ctx.author.id)
        i = await ctx.send("Will you marry me?", view=k)
        k.update_msg(i)

    @commands.command()
    # @commands.cooldown(3, 8, commands.BucketType.user)
    # @commands.has_role(830875873027817484)
    async def screenshot(self, ctx: commands.Context, url: EnsureHTTPConverter):
        await ctx.send(
            embed=nextcord.Embed(
                title="Screenshot",
                description=f"[Open in browser for fast rendering](http://image.thum.io/get/{url})",
                color=nextcord.Color.red(),
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
            color=nextcord.Color.red(),
            title=f"Info about {domain}.is-a.dev",
            description=self.fetch_description_about_a_domain(data),
        )
        await ctx.send(embed=embed, view=k)

    @commands.command()
    async def check(
        self, ctx: commands.Context, domain: SubdomainNameConverter
    ) -> None:
        try:
            await request(
                True,
                "GET",
                f"https://raw.githubusercontent.com/is-a-dev/register/main/domains/{domain}.json",
            )
            await ctx.send(f"Domain {domain} is already taken.")
        except DomainNotExistError:
            await ctx.send(
                "This domain is still available. Claim it before someone take it."
            )


class NonsenseSlash(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @nextcord.slash_command()
    @ac.is_owner()
    async def make_degen(
        self,
        interaction: Interaction,
        user: nextcord.Member = SlashOption(
            description="The degen-like user.", required=True
        ),
        reason=SlashOption(
            description="Why this person should be a degen? Idrk.", required=False
        ),
    ) -> None:

        if reason is None:
            reason = "annoying my Master"
        await user.add_roles(Object(id=1238746465111642122), reason=reason)
        LOG_CHANNEL = cast(
            TextChannel, interaction.guild.get_channel(955105139461607444)
        )
        await LOG_CHANNEL.send(
            f"My Master, MaskDuck, has made {str(user)} (ID {user.id}) for reason {reason}"
        )
        await interaction.send(
            f"Master, I have made {str(user)} a degenerate for {reason}. I'm sorry for all your loss, Master."
        )

    @nextcord.slash_command()
    async def ban(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = SlashOption(
            description="The member to ban", required=True
        ),
        reason: str = SlashOption(description="The reason to ban", required=True),
    ) -> None:
        """Ban somebody of your choosing. Note that this may not work."""
        try:
            await user.send(
                f"You have been banned from **{interaction.guild.name}** for reason: {reason}"
            )
        except HTTPException:
            pass
        await interaction.send(
            f"Banned **{user.display_name}** (ID {user.id}) for reason: **{reason}**"
        )

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
            await interaction.send(f"Domain {domain} is already taken.")
        except DomainNotExistError:
            await interaction.send(
                "This domain is still available. Claim it before someone take it."
            )

    @slash_command()
    async def whois(
        self,
        interaction: Interaction,
        domain: SlashSubdomainNameConverter = SlashOption(
            description="The is-a.dev domain name to find whois for.", required=True
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
                    color=nextcord.Color.red(),
                ),
                view=view,
            )
        except DomainNotExistError:
            await interaction.send("Domain requested cannot be found. Aborting.")

    @slash_command()
    async def report_degenerate(self, interaction: Interaction) -> None:
        await interaction.response.send_modal(ReportDegenModal())

    @slash_command()
    async def propose(self, interaction: Interaction) -> None:
        k = ProposeView(interaction.user.id)
        l = await interaction.send("Will you marry me?", view=k)
        k.update_msg(l)

    @slash_command()
    async def links(self, interaction: Interaction) -> None:
        """Links that are important to this service."""
        k = """Please also check those channels:
        <#991779321758896258> (for an interactive experience go to <#960446827579199488> and type `oc/faq`)
        <#1228996111390343229>
        """
        await interaction.send(k, view=LinkView())

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
                color=nextcord.Color.red(),
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(Nonsense(bot))
    bot.add_cog(NonsenseSlash(bot))
