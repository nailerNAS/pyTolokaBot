from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass
class TolokaResult:
    id: str
    link: str
    title: str
    forum_name: str
    forum_parent: str
    comments: str
    size: str
    seeders: str
    leechers: str
    complete: str

    @staticmethod
    def from_dict(obj: Any) -> 'TolokaResult':
        assert isinstance(obj, dict)

        return TolokaResult(**obj)
