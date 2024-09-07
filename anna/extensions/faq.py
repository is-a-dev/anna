from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

import nextcord
from nextcord.ext import commands


class _QA:
    def __init__(self, question: str, answer: str) -> None:
        self.question: str = question
        self.answer: str = answer


_faq_answer: Dict[str, _QA] = {
    "records": _QA(
        "Which records do you support?",
        "is-a.dev supports A, AAAA, CNAME, MX, TXT and URL records.",
    ),
    "redirect": _QA(
        "Why does my domain still redirect to the is-a.dev website?",
        "The most common solution is clearing your browser's cache. A guide on that can be found here: https://support.google.com/accounts/answer/32050",
    ),
    "waittime": _QA(
        "How long does it take for my domain to get approved?",
        "When we get into it. We always want you to wait for as short as possible. But maintainers cannot always be online. We have school and work, this is just a side project. Just be patient and we'll get to it as soon as possible! For a chance for a quicker review, send your PR in <#1130858271620726784>. Asking when your PR will be approved may result in a mute.",
    ),
    "service": _QA(
        "What services do you support?",
        "We support nearly every service except for Vercel and Netlify.",
    ),
    "nested": _QA(
        "Can I create nested subdomains? (also known as sub-sub domains)",
        "Yes, you can! Simply create a file such as `blog.example.json` and make the file content the same as if you were registering `example.json`. Please note in order to have `blog.example.is-a.dev`, you need to own `example.is-a.dev`.",
    ),
    "staff": _QA(
        "Can I be maintainer/helper?",
        "No, we hand pick every member of our team. You can increase your chances of being chosen by helping out users in <#1155589227728339074>.",
    ),
    "record_not_deployed": _QA(
        "Why are my records not being deployed?",
        "This is a known issue with the CI, however your records should be deployed with-in 24 hours.",
    ),
    "leaked": _QA(
        "I accidently leaked my email or something else, how can I get my PR deleted?",
        "If your PR has not been merged, please DM William with your PR link. If your PR has been merged already, there is nothing we can do about it unfortunately.",
    ),
    "DNS_record_not_showing_up": _QA(
        "My DNS records are not showing up, even after 24 hours.",
        "Please open a thread in <#1155589227728339074> and we will look into it for you.",
    ),
    "privacy_error": _QA(
        "My subdomain shows a privacy error.",
        "This usually happens because your host has not issued a SSL certificate for your subdomain, please wait for it to be issued, or contact your host for further information.",
    ),
}


class FAQDropdown(nextcord.ui.Select):
    if TYPE_CHECKING:
        _message: nextcord.Message | nextcord.PartialInteractionMessage

    def __init__(self):
        options: List[nextcord.SelectOption] = [
            nextcord.SelectOption(
                label="Which records do you support?", value="records"
            ),
            nextcord.SelectOption(
                label="Why does my domain keep redirects to is-a.dev website?",
                value="redirect",
            ),
            nextcord.SelectOption(
                label="How long does it take for my domain to be approved?",
                value="waittime",
            ),
            nextcord.SelectOption(
                label="What services do you support?", value="service"
            ),
            nextcord.SelectOption(
                label="Can I create nested subdomains?", value="nested"
            ),
            nextcord.SelectOption(label="Can I be maintainer/helper?", value="staff"),
            nextcord.SelectOption(
                label="Why are my records not being deployed?",
                value="record_not_deployed",
            ),
            nextcord.SelectOption(
                label="I accidently leaked my email?",
                value="leaked",
            ),
            nextcord.SelectOption(
                label="My DNS records are not showing up, even after 24 hours.",
                value="DNS_record_not_showing_up",
            ),
            nextcord.SelectOption(
                label="My subdomain shows a privacy error.", value="privacy_error"
            ),
        ]
        super().__init__(placeholder="Select your question.", options=options)

    def update_msg(
        self, message: nextcord.Message | nextcord.PartialInteractionMessage
    ):
        self._message: nextcord.Message | nextcord.PartialInteractionMessage = message

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        value = interaction.data["values"][0]  # type: ignore[reportGeneralTypeIssues]
        qa_pair: _QA = _faq_answer.get(value)  # type: ignore[reportAssignmentType]
        embed: nextcord.Embed = nextcord.Embed(
            title=qa_pair.question,
            description=qa_pair.answer,
            color=nextcord.Color.red(),
        )
        await self._message.edit(embed=embed, view=self.view)


class FAQView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=360)  # type: ignore[reportCallIssue]
        self._dropdown = FAQDropdown()
        self.add_item(self._dropdown)

    def update_msg(self, message: nextcord.Message) -> None:
        self._dropdown.update_msg(message)


class FAQ(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.command()  # type: ignore[reportArgumentType]
    async def faq(self, ctx: commands.Context):
        """Show FAQ."""
        k = FAQView()
        embed = nextcord.Embed(
            title="Welcome to FAQ.",
            description="Click the dropdown below to toggle the questions.",
            color=nextcord.Color.blurple(),
        )
        m = await ctx.send(embed=embed, view=k)
        k.update_msg(m)

    @nextcord.slash_command(name="faq")
    async def faq_slash(self, interaction: nextcord.Interaction) -> None:
        """Show FAQ."""
        k = FAQView()
        embed = nextcord.Embed(
            title="Welcome to FAQ.",
            description="Click the dropdown below to toggle the questions.",
            color=nextcord.Color.blurple(),
        )
        m = await interaction.send(embed=embed, view=k)
        k.update_msg(m)  # type: ignore[reportArgumentType]


def setup(bot):
    bot.add_cog(FAQ(bot))
