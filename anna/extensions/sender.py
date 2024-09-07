from nextcord.ext import commands

class sender(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    async def send(self, ctx: commands.Context,args):
        await ctx.send(args)

def setup(bot: commands.Bot):
    bot.add_cog(sender(bot))