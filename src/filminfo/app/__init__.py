from filminfo.app.types import AnyWidget


__ALL__ = ["add_bindtag", "find_ancestor"]


def add_bindtag(widget: AnyWidget, tag: str, position: int = 1) -> None:
    tags = list(widget.bindtags())
    if tag not in tags:
        tags.insert(position, tag)
        widget.bindtags(tuple(tags))


def find_ancestor[T: AnyWidget](widget: AnyWidget | None, cls: type[T]) -> T | None:
    while widget is not None:
        if isinstance(widget, cls):
            return widget

        widget = widget.master

    return None
