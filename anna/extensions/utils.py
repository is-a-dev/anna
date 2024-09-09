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
            
class Purger(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int):
        """Purges a specified number of messages in the channel."""
        
        # Ensure the number is a positive integer
        if amount <= 0:
            await ctx.send("Please specify a positive number of messages to purge.")
            return

        # Perform the purge
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Successfully purged {len(deleted)} messages.", delete_after=5)

def setup(bot: commands.Bot):
    bot.add_cog(Sender(bot))
    bot.add_cog(Purger(bot))
