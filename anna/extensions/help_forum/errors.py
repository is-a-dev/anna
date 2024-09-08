from nextcord.ext import commands, application_checks
import nextcord
from __main__ import Bot


class NoGuildConfig(Exception):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        super().__init__(f"No configuration found for guild id {guild_id}")


class NoThreadFound(Exception):
    def __init__(self, thread_id: int):
        self.thread_id = thread_id
        super().__init__(f"No thread found with id {thread_id}")


class AlreadyClosed(Exception):
    def __init__(self, thread_id: int):
        self.thread_id = thread_id
        super().__init__(f"Thread with id {thread_id} is already closed")


class Errors(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(
        self, interaction: nextcord.Interaction, error: Exception
    ):
        # Proper error handling will be added soon :)
        error = getattr(error, "original", error)
        if isinstance(error, application_checks.errors.ApplicationNotOwner):
            embed = nextcord.Embed(
                title="An Error Occurred",
                description="You must be the owner of this application to use this command.",
                color=nextcord.Color.red(),
            )
            await interaction.send(embed=embed, ephemeral=True)
            return
        else:
            embed = nextcord.Embed(
                title="An Error Occurred",
                description=f"An unexpected error occurred while processing your command. Please report it us.",
                color=nextcord.Color.red(),
            )
            await interaction.send(embed=embed, ephemeral=True)
            self.bot.logger.error(
                f"An error occurred while processing an application command: {error}"
            )
            raise error


def setup(bot: Bot):
    bot.add_cog(Errors(bot))