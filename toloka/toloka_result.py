from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class TolokaResult:
    id: int
    link: str
    title: str
    forum_name: str
    forum_parent: str
    comments: int
    size: str
    seeders: int
    leechers: int
    complete: int

    @staticmethod
    def from_dict(obj: Any) -> 'TolokaResult':
        assert isinstance(obj, dict)
        id = int(from_str(obj.get("id")))
        link = from_str(obj.get("link"))
        title = from_str(obj.get("title"))
        forum_name = from_str(obj.get("forum_name"))
        forum_parent = from_str(obj.get("forum_parent"))
        comments = int(from_str(obj.get("comments")))
        size = from_str(obj.get("size"))
        seeders = int(from_str(obj.get("seeders")))
        leechers = int(from_str(obj.get("leechers")))
        complete = int(from_str(obj.get("complete")))
        return TolokaResult(id, link, title, forum_name, forum_parent, comments, size, seeders, leechers, complete)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(str(self.id))
        result["link"] = from_str(self.link)
        result["title"] = from_str(self.title)
        result["forum_name"] = from_str(self.forum_name)
        result["forum_parent"] = from_str(self.forum_parent)
        result["comments"] = from_str(str(self.comments))
        result["size"] = from_str(self.size)
        result["seeders"] = from_str(str(self.seeders))
        result["leechers"] = from_str(str(self.leechers))
        result["complete"] = from_str(str(self.complete))
        return result


def toloka_result_from_dict(s: Any) -> TolokaResult:
    return TolokaResult.from_dict(s)


def toloka_result_to_dict(x: TolokaResult) -> Any:
    return to_class(TolokaResult, x)
