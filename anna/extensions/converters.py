from __future__ import annotations

from typing import Final, Tuple

from nextcord import Interaction, OptionConverter
from nextcord.ext import commands

__all__: Final[Tuple[str]] = (
    "SubdomainNameConverter",
    "SlashSubdomainNameConverter",
    "EnsureHTTPConverter",
    "SlashEnsureHTTPConverter",
    "RGBColorTupleConverter",
)


class SubdomainNameConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> str:  # type: ignore
        argument = argument.lower()
        if argument.endswith(".is-a.dev"):
            return argument[:-9]
        return argument


class RGBColorTupleConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> Tuple[str]:  # type: ignore
        return argument.split("-")  # type: ignore[reportReturnType]


class SlashSubdomainNameConverter(OptionConverter):
    async def convert(self, interaction: Interaction, value: str) -> str:  # type: ignore
        value = value.lower()
        if value.endswith(".is-a.dev"):
            return value[:-9]
        return value


class SlashEnsureHTTPConverter(OptionConverter):
    async def convert(self, interaction: Interaction, value: str) -> str:  # type: ignore
        if value.startswith("https://") or value.startswith("http://"):
            return value
        return "http://" + value


class EnsureHTTPConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> str:  # type: ignore
        if argument.startswith("https://") or argument.startswith("http://"):
            return argument
        return "http://" + argument


class EnsureNoHTTPConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> str:  # type: ignore[reportUnusedArgument]
        if argument.startswith("https://"):
            return argument[len("https://") - 1 :]

        if argument.startswith("http://"):
            return argument[len("http://") - 1 :]

        return argument


class SlashEnsureNoHTTPConverter(commands.Converter):
    async def convert(self, interaction: Interaction, argument: str) -> str:  # type: ignore[reportUnusedArgument]
        if argument.startswith("https://"):
            return argument[len("https://") - 1 :]

        if argument.startswith("http://"):
            return argument[len("http://") - 1 :]

        return argument
