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

from typing import List, Literal, TypedDict, Union

from typing_extensions import NotRequired

RecordType = Literal["A", "CNAME", "MX", "URL", "TXT"]


class _OwnerObject(TypedDict):
    username: str
    email: str

    # known accounts
    discord: NotRequired[str]
    twitter: NotRequired[str]


class _OtherRecordObject(TypedDict, total=False):
    A: List[str]
    URL: str
    TXT: Union[str, List[str]]
    MX: List[str]


class _CNAMERecordObject(TypedDict):
    CNAME: str


_RecordObject = Union[_OtherRecordObject, _CNAMERecordObject]


class Domain(TypedDict):
    description: NotRequired[str]
    repo: NotRequired[str]
    owner: _OwnerObject
    record: _RecordObject
