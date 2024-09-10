import re
from nextcord.ext import commands
import nextcord

class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    async def send(self, ctx: commands.Context, *, message: str):
        """Send a message as Anna."""
        words = message.split()

        if len(words) > 0:
            first_word = words[0]
            if first_word.startswith("<#") and first_word.endswith(">"):
                channel_id = int(first_word[2:-1])
                channel = self._bot.get_channel(channel_id)

                if isinstance(channel, nextcord.TextChannel):
                    message_content = ' '.join(words[1:])
                    if message_content:
                        await channel.send(message_content)
                    else:
                        await ctx.send("No message content to send.")
                else:
                    await ctx.send("Invalid channel.")
            else:
                await ctx.send(message)
        else:
            await ctx.send("Please provide a message to send.")
            
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
        await ctx.send(f"Successfully purged {len(deleted)} messages.", delete_after=3)

def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))
