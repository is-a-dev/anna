#Copyright (c) 2024 - present, MaskDuck

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

#3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations

import black
import nextcord
from nextcord import Interaction, SlashOption, slash_command, ui
from nextcord.ext import commands


class FormatModal(ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Format code", timeout=900)
        self.code_to_format = ui.TextInput(
            label="Code to format",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
        )
        self.add_item(self.code_to_format)

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        response = black.format_str(self.code_to_format.value, mode=black.Mode())  # type: ignore -- it is required lmao
        await interaction.send(
            embed=nextcord.Embed(
                title="Formatted code",
                description=f"```py\n{response}\n```",
                color=nextcord.Color.green(),
            )
        )


class Format(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @slash_command()
    async def format_code(self, interaction: Interaction) -> None:  # type: ignore
        pass

    @format_code.subcommand(name="black")
    async def black_(
        self,
        interaction: Interaction,
        code=SlashOption(description="Code to format", required=False),
    ) -> None:
        """Format code with Black."""
        if not code:
            return await interaction.response.send_modal(FormatModal())
        await interaction.response.defer()

        response = black.format_str(code, mode=black.Mode())
        await interaction.send(
            embed=nextcord.Embed(
                title="Formatted code",
                description=f"```py\n{response}\n```",
                color=nextcord.Color.green(),
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(Format(bot))
    return
