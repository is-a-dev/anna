import nextcord
from nextcord.ext import commands

class Starboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        starboard_channel_id = 1274682244619042856
        starboard_channel = self.bot.get_channel(starboard_channel_id)

        # Fetch the message details
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        message = await channel.fetch_message(payload.message_id)

        # Check if any emoji has 4 or more reactions
        for reaction in message.reactions:
            if reaction.count >= 4:
                # Create the embed with the message content and other details
                embed = nextcord.Embed(
                    title="Starred Message",
                    description=message.content or "[No Content]",
                    color=nextcord.Color.gold()
                )
                embed.add_field(name="Author", value=message.author.mention, inline=True)
                embed.add_field(
                    name="Link to Message", 
                    value=f"[Jump to Message]({message.jump_url})", 
                    inline=True
                )
                embed.set_footer(text=f"Channel: {channel.name} | Emoji: {reaction.emoji}")
                
                # Send the embed to the starboard channel
                await starboard_channel.send(embed=embed)
                break

def setup(bot: commands.Bot):
    bot.add_cog(Starboard(bot))
