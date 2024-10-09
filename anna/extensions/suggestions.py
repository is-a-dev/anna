"""
BSD 3-Clause License

Copyright (c) 2024 - present, MaskDuck

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

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
            await interaction.send(
                "You must be in the suggestions channel to use this command.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(ApproveOrDeny(True, message))

    @message_command(name="Deny the suggestion")
    @application_checks.has_role(830875873027817484)
    async def deny_suggestion_msg(
        self, interaction: Interaction, message: Message
    ) -> None:
        if interaction.channel.id != self.suggestion_channel:
            await interaction.send(
                "You must be in the suggestions channel to use this command.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(ApproveOrDeny(False, message))

    @slash_command(name="suggestion")
    async def _suggestion(self, interaction: Interaction):  # type: ignore[reportUnusedVariable]
        pass

    @_suggestion.subcommand(
        name="suggest", description="We'd love to hear your suggestions!"
    )
    async def _suggest(
        self,
        interaction: Interaction,
        for_: str = SlashOption(
            name="for",
            description="Is your suggestion regarding the server or service for?",
            required=True,
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
                "Please select what your suggestion is for.", ephemeral=True
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
        name="deny", description="[MAINTAINER ONLY] Deny suggestion"
    )
    @application_checks.has_permissions(administrator=True)
    async def _deny(
        self,
        interaction: Interaction,
        messageId: str = SlashOption(
            name="message_id", description="Message to deny", required=True
        ),
        why: str = SlashOption(
            name="why", description="Why did you deny this suggestion?", required=True
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
        await interaction.send(
            f"Denied suggestion https://discord.com/channels/830872854677422150/{self.suggestion_channel}/{messageId}.",
            ephemeral=True,
        )

    @_suggestion.subcommand(
        name="approve", description="[MAINTAINER ONLY] approve suggestion"
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

        await interaction.send(
            f"Approved suggestion https://discord.com/channels/830872854677422150/{self.suggestion_channel}/{messageId}.",
            ephemeral=True,
        )


def setup(bot):
    bot.add_cog(Suggestion(bot))
