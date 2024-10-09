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
