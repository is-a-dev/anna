from nextcord.ext import commands


class Testings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def hinder(self, ctx: commands.Context, cmd: str):
        if cmd == "hinder":
            await ctx.send("I did not expect you to be such a fool")
        else:
            command = self._bot.get_command(cmd)
            if command is None:
                await ctx.send("Command not found.")
                return
            command.enabled = not command.enabled
            await ctx.send("Request satisfied, master.")

    @commands.command()
    @commands.is_owner()
    async def test_owner_perm(self, ctx: commands.Context):
        await ctx.send("Master, how can I help you?")

    @commands.command()
    @commands.is_owner()
    async def reload_slash_command(self, ctx: commands.Context) -> None:
        await ctx.bot.sync_application_commands()
        await ctx.send("Request satisfied, master.")

    @commands.command()
    @commands.has_role(830875873027817484)
    async def disable_oneword_cog(self, ctx: commands.Context) -> None:
        try:
            self._bot.unload_extension("extensions.oneword")
        except commands.ExtensionNotLoaded:
            await ctx.send("Oneword cog not already loaded.")
        await ctx.send(
            "Unloaded extension. Please ask my master to reload the cog if needed."
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Testings(bot))
