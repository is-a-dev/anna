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
