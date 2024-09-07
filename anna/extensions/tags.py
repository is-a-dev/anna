# ruff: noqa
from nextcord.ext import commands

nohelp = """
Hey you! This is not a help channel!\n
We have a help channel for a reason, <#1228996111390343229>.\n
Please use that as a help channel. We need you to open a thread, even if it is a tiny problem.\n
So... **Enjoy troll answers past this message and take them with a pinch of salt. The action of following any help in this channel past this message is at your own risk. You've been warned.**\n
Please check the [is-a.dev docs](https://www.is-a.dev/docs/)\n
Have fun!"""

waittime = """
Because my ancestor, orangc, is a degenerate and the maintainers are busy dealing with him, we are unable to provide you immediate assistance.
ETA for merging varies between a second to a eternity.
Remember, a watched pot never boils, so why don't get your other work done and maybe your is-a.dev PR will be merged in that time? Hyper-hyper-efficient time management!
Maintainers shouldn't be spending all their time merging PRs and neither should you spend all your time waiting for it.
"""

rtfm = """
Please read the damned docs. It exists for a reason.\n
Our maintainers and helpers are volunteers. It's not our job to answer stupid questions already answered in the documentation or FAQ.\n
- [is-a.dev documentation](https://is-a.dev/docs)\n
- <#991779321758896258>\n
"""
domservice = """
is-a.dev can give you support with your ***domain***, and that's provided you've read the [documentation](https://is-a.dev/docs).\n
We do __not__ provide support for anything else. We aren't an HTML boot camp, it's not our job to teach you JSON. And we don't provide support for Github or DNS questions either.
"""


class Tags(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.command()
    async def nohelp(self, ctx):
        if ctx.channel.id in [830872854677422153, 1057228967972716584]:
            embed = nextcord.Embed(
                title="Please... this is not a help channel",
                description=nohelp,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)
        else:
            msg = await ctx.send("You fool.")
            await msg.delete()

    @commands.command()
    async def waittime(self, ctx):
        if True:  # blame orangc
            embed = nextcord.Embed(
                title="How long is it until my PR is merged?",
                description=waittime,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def rtfm(self, ctx):
        if True:
            embed = nextcord.Embed(
                title="Read The Fucking Manual",
                description=rtfm,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def domservice(self, ctx):
        if True:
            embed = nextcord.Embed(
                title="We're a domain service, and we provide support for domains",
                description=domservice,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tags(bot))
