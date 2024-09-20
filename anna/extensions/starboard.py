import nextcord
from motor.motor_asyncio import AsyncIOMotorClient
import os
from nextcord.ext import commands

class Starboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = AsyncIOMotorClient(os.getenv("MONGO")).get_database("anna")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        starboard_channel_id = 1274682244619042856 
        starboard_channel = self.bot.get_channel(starboard_channel_id)

        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        
        whitelisted_channels = await self.db.starboard_whitelist.find_one({"whitelist": {"$in": [channel.id]}})
        if not whitelisted_channels:
            return

        message = await channel.fetch_message(payload.message_id)
        emoji_reaction = None
        for reaction in message.reactions:
            if str(reaction.emoji) == str(payload.emoji):
                emoji_reaction = reaction
                break

        # at least 4 reactions
        if emoji_reaction and emoji_reaction.count >= 4:
            existing_star_message = await self.db.starboard.find_one({"message_id": message.id})

            if existing_star_message:
                # Edit the existing starboard message
                starboard_message = await starboard_channel.fetch_message(existing_star_message['starboard_message_id'])
                embed = self._create_embed(message, emoji_reaction)
                await starboard_message.edit(embed=embed)
            else:
                # Create a new starboard entry
                embed = self._create_embed(message, emoji_reaction)
                starboard_message = await starboard_channel.send(embed=embed)

                # Save the starboard message ID to the database
                await self.db.starboard.insert_one({
                    "message_id": message.id,
                    "starboard_message_id": starboard_message.id
                })

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def starboard_whitelist(self, ctx: commands.Context, action: str):
        """Add or remove the current channel from the starboard whitelist."""
        channel_id = ctx.channel.id
        whitelist_data = await self.db.starboard_whitelist.find_one({"name": "whitelist"})

        if action == "add":
            if channel_id in whitelist_data['whitelist']:
                await ctx.send("This channel is already whitelisted for starboard.")
                return
            
            await self.db.starboard_whitelist.update_one(
                {"name": "whitelist"},
                {"$addToSet": {"whitelist": channel_id}},
                upsert=True
            )
            await ctx.send(f"{ctx.channel.mention} has been added to the starboard whitelist.")
        
        elif action == "remove":
            if channel_id not in whitelist_data['whitelist']:
                await ctx.send("This channel is not whitelisted for starboard.")
                return
            
            await self.db.starboard_whitelist.update_one(
                {"name": "whitelist"},
                {"$pull": {"whitelist": channel_id}}
            )
            await ctx.send(f"{ctx.channel.mention} has been removed from the starboard whitelist.")
        
        else:
            await ctx.send("Invalid action! Use `add` to whitelist or `remove` to un-whitelist the channel.")
        
    def _create_embed(self, message: nextcord.Message, reaction: nextcord.Reaction):
        """Helper function to create the starboard embed."""
        embed = nextcord.Embed(
            title="Starred Message",
            description=message.content or "[No Content]",
            color=nextcord.Color.blue()
        )
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(
            name="Link to Message", 
            value=f"[Jump to Message]({message.jump_url})", 
            inline=True
        )
        embed.set_footer(text=f"Channel: {message.channel.name} | Emoji: {reaction.emoji} | Reactions: {reaction.count}")
        return embed

def setup(bot: commands.Bot):
    bot.add_cog(Starboard(bot))
