import re
import nextcord
from nextcord.ext import commands

GITHUB_URL_PATTERN = r"https:\/\/github.com\/([A-Za-z0-9-]+)\/([A-Za-z0-9-]+)(\/pull|\/issues)?(#|\/)(?P<pr_id>\d+)"
SHORT_PR_PATTERN = r"##(\d+)"


class PRChannelMessageCleaner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = 1130858271620726784
        self.exempt_role_id = 1197475623745110109

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        if message.channel.id != self.target_channel_id:
            return

        if any(role.id == self.exempt_role_id for role in message.author.roles):
            return

        if re.search(GITHUB_URL_PATTERN, message.content) or re.search(
            SHORT_PR_PATTERN, message.content
        ):
            return

        await message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(PRChannelMessageCleaner(bot))
