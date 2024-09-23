# Copyright (c) 2024 - present, MaskDuck

from __future__ import annotations

import logging
from string import ascii_letters
from typing import TYPE_CHECKING, Final

from nextcord import Interaction, Member, user_command
from nextcord.ext import application_checks as ac
from nextcord.ext import commands

if TYPE_CHECKING:
    import nextcord


NUMBERS: Final[str] = "1234567890"
normal_characters: Final[str] = ascii_letters + NUMBERS


class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        try:
            assert self._bot.intents.auto_moderation is True
        except AssertionError:
            logging.getLogger("nextcord").warn(
                "auto_moderation intents is not enabled. Fix it or else no nword notifications."
            )

    @commands.Cog.listener("on_member_join")
    async def check_nickname_on_join(self, member: nextcord.Member) -> None:
        if member.display_name[0] not in normal_characters:
            await member.edit(
                nick="Moderated Nickname",
                reason="Hoisting is not allowed in our server. —Automoderation set by Anna.",
            )

    @commands.Cog.listener("on_member_update")
    async def check_nickname_on_edit(
        self, _: nextcord.Member, after: nextcord.Member
    ) -> None:
        if after.display_name[0] not in normal_characters:
            await after.edit(
                nick="Moderated Nickname",
                reason="Hoisting is not allowed in our server. —Automoderation set by Anna.",
            )

    @user_command(
        dm_permission=False, name="Cleanse Nickname", default_member_permissions=8
    )
    @ac.has_role(830875873027817484)
    async def cleanse_nickname(self, interaction: Interaction, member: Member) -> None:
        previous_display_name = member.display_name
        await member.edit(
            nick="Moderated Nickname",
            reason=f"nickname cleansing requested by {interaction.user.display_name}",
        )
        await interaction.send(
            f"Nickname of {previous_display_name} has been cleansed to `Moderated Nickname`."
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AutoMod(bot))
