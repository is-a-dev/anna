import re
import nextcord
from nextcord.ext import commands
from __main__ import EMBED_COLOR

GITHUB_URL_PATTERN = r"https:\/\/github.com\/([A-Za-z0-9-]+)\/([A-Za-z0-9-]+)(\/pull|\/issues)?(#|\/)(?P<pr_id>\d+)"
SHORT_PR_PATTERN = r"##(\d+)"


class PR_Channel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = 1130858271620726784
        self.exempt_role_id = 1197475623745110109
        self.sticky_message = None

    @commands.Cog.listener()
    async def on_ready(self):
        """Send the sticky message when the bot is ready."""
        channel = self.bot.get_channel(self.target_channel_id)
        if channel:
            await self.send_sticky_message(channel)

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        # Always resend the sticky message on any message
        if message.channel.id == self.target_channel_id:
            await self.send_sticky_message(message.channel)

        # If the author is the bot, no further checks needed
        if message.author.bot:
            return

        # Only process messages in the target channel
        if message.channel.id != self.target_channel_id:
            return

        # Check if the user has the exempt role
        if any(role.id == self.exempt_role_id for role in message.author.roles):
            return

        # Suppress embeds in the message
        await self.suppress_embeds(message)

        # If the message contains a valid GitHub link or PR pattern, do nothing
        if re.search(GITHUB_URL_PATTERN, message.content) or re.search(SHORT_PR_PATTERN, message.content):
            return

        # If the message doesn't match the pattern, delete it
        await message.delete()

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        """Re-send the sticky message when a message is deleted."""
        if message.channel.id == self.target_channel_id:
            await self.send_sticky_message(message.channel)

    async def suppress_embeds(self, message: nextcord.Message):
        """Suppress the embeds of a message."""
        try:
            await message.edit(suppress=True)
        except nextcord.Forbidden:
            pass  # Handle permission errors gracefully

    async def send_sticky_message(self, channel: nextcord.TextChannel):
        """Ensure that the sticky message is always at the bottom."""
        if self.sticky_message:
            try:
                await self.sticky_message.delete()
            except nextcord.NotFound:
                pass  # Sticky message was already deleted
        
        embed = nextcord.Embed(
            description="Please only send PR links in this channel, all other messages are automatically deleted. <:salute:1287332162189922366>",
            color=EMBED_COLOR,
        )
        self.sticky_message = await channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(PR_Channel(bot))
