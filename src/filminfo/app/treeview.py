import tkinter as tk
from tkinter import ttk

from filminfo.app.types import AnyWidget


class CustomTreeview(ttk.Treeview):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        def _on_shift_click(event: tk.Event) -> str | None:
            region = self.identify("element", event.x, event.y)
            if region != "Treeitem.indicator":
                return None

            item = self.identify_row(event.y)
            if not item:
                return None

            if int(event.state) & 0x0001:
                if self.item(item, "open"):
                    self.collapse_all(item)
                else:
                    self.expand_all(item)
                return "break"

            return None

        self.bind("<Button-1>", _on_shift_click, add="+")

    def expand_all(self, item: str | int | None = None) -> None:
        if item:
            self.item(item, open=True)
        for child in self.get_children(item):
            self.expand_all(child)

    def collapse_all(self, item: str | int | None = None) -> None:
        if item:
            self.item(item, open=False)
        for child in self.get_children(item):
            self.collapse_all(child)
