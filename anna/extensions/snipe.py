import discord
from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        self.sniped_messages[message.channel.id] = {
            "content": message.content,
            "author": message.author,
            "time": message.created_at
        }

    @commands.command(name="snipe")
    async def snipe(self, ctx: commands.Context):
        sniped_message = self.sniped_messages.get(ctx.channel.id)

        if not sniped_message:
            await ctx.send("There's nothing to snipe!")
            return

        embed = discord.Embed(
            description=sniped_message["content"],
            color=discord.Color.red(),
            timestamp=sniped_message["time"]
        )
        embed.set_author(name=f"{sniped_message['author'].display_name}", icon_url=sniped_message['author'].avatar.url)
        embed.set_footer(text=f"Deleted in #{ctx.channel.name}")

        await ctx.send(embed=embed)

    @snipe.error
    async def snipe_error(self, ctx: commands.Context, error):
        await ctx.send("An unknown error occurred.")

def setup(bot):
    bot.add_cog(Snipe(bot))