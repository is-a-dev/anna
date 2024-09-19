import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

class Counting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        # Fetch the counting channel and the current count
        counting_channel_id = 1281898370134183950
        counting_channel = self.bot.get_channel(counting_channel_id)

        if message.channel.id != counting_channel_id:
            return

        # Get the last message count from the database
        current_count = await self.db.counting.find_one({"channel_id": counting_channel_id})

        if not current_count:
            await self.db.counting.insert_one({"channel_id": counting_channel_id, "count": 0})
            current_count = {"count": 0}

        last_number = current_count['count']

        # Check if the message content is the next number
        try:
            next_number = int(message.content)
            if next_number == last_number + 1:
                await self.db.counting.update_one(
                    {"channel_id": counting_channel_id},
                    {"$set": {"count": next_number}}
                )

                await self.db.leaderboard.update_one(
                    {"user_id": message.author.id},
                    {"$inc": {"count": 1}},
                    upsert=True
                )

            else:
                await message.delete()

        except ValueError:
            await message.delete()

    @commands.command()
    @commands.is_owner()
    async def set_count(self, ctx: commands.Context, count: int):
        """Allows bot owner to set the current count in the counting channel."""
        counting_channel_id = 1281898370134183950

        await self.db.counting.update_one(
            {"channel_id": counting_channel_id},
            {"$set": {"count": count}}
        )
        await ctx.send(f"The count has been set to {count}.")

    @commands.command()
    @commands.is_owner()
    async def set_score(self, ctx: commands.Context, member: nextcord.Member, score: int):
        """Allows bot owner to change the score of users in the leaderboard."""
        await self.db.leaderboard.update_one(
            {"user_id": member.id},
            {"$set": {"count": score}}
        )
        await ctx.send(f"{member.display_name}'s score has been set to {score}.")

    @nextcord.slash_command(name="leaderboard", description="Displays the leaderboard of top counters.")
    async def leaderboard(self, interaction: Interaction):
        """Slash command to show the leaderboard in an embed."""
        leaderboard_data = self.db.leaderboard.find().sort("count", -1).limit(10)
        leaderboard_list = await leaderboard_data.to_list(length=10)

        if not leaderboard_list:
            await interaction.response.send_message("No one is on the leaderboard yet!", ephemeral=True)
            return

        embed = nextcord.Embed(title="Counting Leaderboard", color=nextcord.Color.blue())
        for idx, entry in enumerate(leaderboard_list, start=1):
            user = self.bot.get_user(entry['user_id'])
            username = user.display_name if user else "Unknown User"
            embed.add_field(
                name=f"{idx}. {username}",
                value=f"Count: {entry['count']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

# Setup the cog
def setup(bot: commands.Bot):
    bot.add_cog(Counting(bot))
