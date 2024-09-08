import re
from nextcord.ext import commands
import nextcord

class Sender(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    async def send(self, ctx: commands.Context, *, message: str):
        channel_mention = re.match(r"<#(\d+)>", message.split()[0])
        
        if channel_mention:
            channel_id = int(channel_mention.group(1))
            channel = self._bot.get_channel(channel_id)
            if channel:
                message_content = message.split(' ', 1)[1] if len(message.split(' ', 1)) > 1 else ""
                await channel.send(message_content)
            else:
                await ctx.send("Invalid channel.")
        else:
            await ctx.send(message)

def setup(bot: commands.Bot):
    bot.add_cog(Sender(bot))
