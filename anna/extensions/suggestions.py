from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Literal, cast

from nextcord import (
    Colour,
    Embed,
    Interaction,
    Message,
    SlashOption,
    TextChannel,
    TextInputStyle,
    message_command,
    slash_command,
)
from nextcord.errors import InteractionResponded
from nextcord.ext import application_checks, commands

# from models.basecog import BaseCog

if TYPE_CHECKING:
    pass

from nextcord import ui


class ApproveOrDeny(ui.Modal):
    def __init__(self, mode: bool, message: Message) -> None:
        self._suggestion_msg: Message = message
        if mode:
            title = "Approve the suggestion"
        else:
            title = "Deny the suggestion"
        self._mode: bool = mode
        super().__init__(title=title, timeout=180)
        self.reas = ui.TextInput(
            label="Give a reason.", style=TextInputStyle.paragraph, required=True
        )
        self.add_item(self.reas)

    async def callback(self, interaction: Interaction) -> None:
        embed = self._suggestion_msg.embeds[0]
        embed.add_field(
            name=f"{'Approved by' if self._mode else 'Denied by'} {str(interaction.user)}",
            value=self.reas.value,
        )
        await self._suggestion_msg.edit(embed=embed)


class Suggestion(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.suggestion_channel = 1236200920317169695

    suggestion_mode = ["the server", "the service"]

    @message_command(name="Approve the suggestion")
    @application_checks.has_role(830875873027817484)
    async def approve_suggestion_msg(
        self, interaction: Interaction, message: Message
    ) -> None:
        if interaction.channel.id != self.suggestion_channel:
            await interaction.send("You fucked up life. Good job!")
            return
        await interaction.response.send_modal(ApproveOrDeny(True, message))

    @message_command(name="Deny the suggestion")
    @application_checks.has_role(830875873027817484)
    async def deny_suggestion_msg(
        self, interaction: Interaction, message: Message
    ) -> None:
        if interaction.channel.id != self.suggestion_channel:
            await interaction.send("You fucked up life. Good job!")
            return
        await interaction.response.send_modal(ApproveOrDeny(False, message))

    @slash_command(name="suggestion")
    async def _suggestion(self, interaction: Interaction):  # type: ignore[reportUnusedVariable]
        pass

    @_suggestion.subcommand(
        name="suggest", description="We'd love to hear your suggestion!"
    )
    async def _suggest(
        self,
        interaction: Interaction,
        for_: str = SlashOption(
            name="for", description="What do you want to suggest for?", required=True
        ),
        suggestion: str = SlashOption(
            name="suggestion", description="Write your suggestion here.", required=True
        ),
    ):
        embed: Embed

        for_ = cast(Literal["the server", "the service"], for_)
        if for_ == "the server":
            embed = Embed(
                title="Server Suggestion", description=suggestion, colour=Colour.red()
            )
            embed.set_footer(
                text=f"By {str(interaction.user)} (ID {interaction.user.id})"
            )

        elif for_ == "the service":
            embed = Embed(
                title="Service Suggestion", description=suggestion, colour=Colour.red()
            )
            embed.set_footer(
                text=f"By {str(interaction.user)} (ID {interaction.user.id})"
            )

        else:
            await interaction.send(
                "Well, what do you want to suggest for? Use your brain and let autocomplete guide you."
            )

        channel = interaction.guild.get_channel(self.suggestion_channel)
        channel = cast(TextChannel, channel)
        message = await channel.send(embed=embed)  # type: ignore
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        log_channel = self.bot.get_channel(955105139461607444)
        log_channel = cast(TextChannel, log_channel)
        await log_channel.send(f"{str(interaction.user)} has suggested {suggestion}.")
        await interaction.send(
            f"You can now see your suggestion in {channel.mention}.",
            ephemeral=True,
        )

    @_suggest.on_autocomplete("for_")
    async def _on_suggest_for_autocomplete(self, interaction: Interaction, for_: str):
        with suppress(InteractionResponded):
            if not for_:
                await interaction.response.send_autocomplete(self.suggestion_mode)

            nearest_mode = [
                mode
                for mode in self.suggestion_mode
                if for_.lower().startswith(mode.lower())
            ]
            await interaction.response.send_autocomplete(nearest_mode)

    @_suggestion.subcommand(
        name="deny", description="[MAINTAINER ONLY] disapprove the suggestion :("
    )
    @application_checks.has_permissions(administrator=True)
    async def _deny(
        self,
        interaction: Interaction,
        messageId: str = SlashOption(
            name="message_id", description="Message to deny", required=True
        ),
        why: str = SlashOption(
            name="why", description="Why did you deny this request?", required=True
        ),
    ):
        channel = interaction.guild.get_channel(self.suggestion_channel)
        channel = cast(TextChannel, channel)
        message = await channel.fetch_message(int(messageId))
        embed = message.embeds[0]
        new_embed = embed.add_field(
            name=f"Denied by {str(interaction.user)}", value=why
        )
        await message.edit(embed=new_embed)
        await interaction.send("Done.")

    @_suggestion.subcommand(
        name="approve", description="[MAINTAINER ONLY] approve the suggestion :)"
    )
    @application_checks.has_permissions(administrator=True)
    async def _approve(
        self,
        interaction: Interaction,
        messageId: str = SlashOption(
            name="message_id", description="Message to approve", required=True
        ),
        why: str = SlashOption(
            name="why", description="Why did you deny this request?", required=False
        ),
    ):
        if not why:
            why = "No reason provided"
        channel = self.bot.get_channel(self.suggestion_channel)
        channel = cast(TextChannel, channel)
        message = await channel.fetch_message(int(messageId))
        embed = message.embeds[0]
        new_embed = embed.add_field(
            name=f"Approved by {str(interaction.user)}", value=why
        )
        await message.edit(embed=new_embed)

        await interaction.send("Done.")


def setup(bot):
    bot.add_cog(Suggestion(bot))
