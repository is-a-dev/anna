import nextcord
from nextcord.errors import InteractionResponded
from nextcord.ext import application_checks, commands
from nextcord import ui
from __main__ import EMBED_COLOR

SUGGESTION_CHANNEL_ID = 1236200920317169695
MAINTAINER_ROLE_ID = 830875873027817484
ERROR_COLOR = 0xFF0037


class ApproveOrDeny(ui.Modal):
    def __init__(self, mode: bool, message: nextcord.Message) -> None:
        self._suggestion_msg: nextcord.Message = message
        title = "Approve Suggestion" if mode else "Deny Suggestion"
        self._mode: bool = mode
        super().__init__(title=title, timeout=180)
        self.reason = ui.TextInput(
            label="Provide a reason:",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
        )
        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        embed = self._suggestion_msg.embeds[0]
        embed.add_field(
            name=f"{'Approved by' if self._mode else 'Denied by'} {interaction.user}",
            value=self.reason.value,
        )
        await self._suggestion_msg.edit(embed=embed)
        embed = nextcord.Embed(
            description="Action completed successfully.", colour=EMBED_COLOR
        )
        await interaction.send(embed=embed, ephemeral=True)


class Suggestion(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.suggestion_channel = SUGGESTION_CHANNEL_ID

    @nextcord.message_command(name="Approve Suggestion")
    @application_checks.has_role(MAINTAINER_ROLE_ID)
    async def approve_suggestion_msg(
        self, interaction: nextcord.Interaction, message: nextcord.Message
    ) -> None:
        if interaction.channel.id != self.suggestion_channel:
            error_embed = nextcord.Embed(
                description="You must be in the suggestions channel to use this command.",
                colour=ERROR_COLOR,
            )
            await interaction.send(embed=error_embed, ephemeral=True)
            return
        await interaction.response.send_modal(ApproveOrDeny(True, message))

    @nextcord.message_command(name="Deny Suggestion")
    @application_checks.has_role(MAINTAINER_ROLE_ID)
    async def deny_suggestion_msg(
        self, interaction: nextcord.Interaction, message: nextcord.Message
    ) -> None:
        if interaction.channel.id != self.suggestion_channel:
            error_embed = nextcord.Embed(
                description="You must be in the suggestions channel to use this command.",
                colour=ERROR_COLOR,
            )
            await interaction.send(embed=error_embed, ephemeral=True)
            return
        await interaction.response.send_modal(ApproveOrDeny(False, message))

    @nextcord.slash_command(name="suggestion")
    async def _suggestion(self, interaction: nextcord.Interaction):
        pass

    @_suggestion.subcommand(name="submit", description="Submit your suggestion!")
    async def submit_suggestion(
        self,
        interaction: nextcord.Interaction,
        suggestion: str = nextcord.SlashOption(
            name="suggestion", description="Enter your suggestion.", required=True
        ),
    ):
        embed = nextcord.Embed(
            description=suggestion,
            colour=EMBED_COLOR,
        )
        embed.set_footer(
            text=f"Suggested by {interaction.user} (ID: {interaction.user.id})"
        )

        channel = interaction.guild.get_channel(self.suggestion_channel)
        channel = cast(nextcord.TextChannel, channel)
        message = await channel.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        embed = nextcord.Embed(
            description=f"Your suggestion has been submitted in {channel.mention}.",
            colour=EMBED_COLOR,
        )
        await interaction.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Suggestion(bot))
