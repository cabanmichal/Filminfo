import json
import re
import tkinter as tk
from tkinter import messagebox, ttk

from filminfo.app.scrollable_frame import ScrollableFrame
from filminfo.app.treeview import CustomTreeview
from filminfo.app.types import AnyWidget
from filminfo.configuration import (
    APP_NAME,
    DEFAULT_WIN_SIZE,
    MIN_WIN_SIZE,
    PADDING_BIG,
    PADDING_MEDIUM,
    PADDING_SMALL,
)


class MetadataView(ttk.Frame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._metadata: str = "[]"
        self._tree_items: list[tuple[str, str]] = []
        self._filter_applied = False

        # --- Elements ---
        self._scrollable = ScrollableFrame(self)
        self._tree = CustomTreeview(
            self._scrollable.container,
            columns=("group", "tag", "value"),
            selectmode="browse",
        )
        self._label_data = ttk.Label(self, text="Metadata:")
        self._button_expand = ttk.Button(
            self, text="Expand all", command=self._on_expand_all
        )
        self._button_collapse = ttk.Button(
            self, text="Collapse all", command=self._on_collapse_all
        )

        self._label_filter = ttk.Label(self, text="Filter by regex:")
        self._pattern_var = tk.StringVar()
        self._entry_filter = ttk.Entry(self, textvariable=self._pattern_var)
        self._button_filter_apply = ttk.Button(
            self, text="Apply", command=self._on_filter_apply
        )
        self._button_filter_clear = ttk.Button(
            self, text="Clear", command=self._on_filter_clear
        )

        self._button_clone = ttk.Button(
            self, text="To new window", command=self._on_clone
        )

        self._layout()
        self.__configure()

    def _layout(self) -> None:
        self._label_data.grid(row=0, column=0, sticky="w")
        self._button_expand.grid(row=1, column=0, sticky="w", padx=(0, PADDING_SMALL))
        self._button_collapse.grid(row=1, column=1, sticky="w", padx=PADDING_SMALL)
        self._button_clone.grid(row=1, column=6, sticky="e", padx=(PADDING_SMALL, 0))

        self._scrollable.grid(row=2, column=0, sticky="nsew", columnspan=7)
        self._tree.grid(row=0, column=0)

        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)

    def __configure(self) -> None:
        self._tree.heading("#0", text="Filename")
        self._tree.heading("group", text="Group")
        self._tree.heading("tag", text="Tag name")
        self._tree.heading("value", text="Value")
        self._tree.column("#0", width=260, stretch=False)
        self._tree.column("group", width=100, stretch=False)
        self._tree.column("tag", width=200, stretch=False)
        self._tree.column("value", width=2_000, stretch=True)
        self._tree.bind("<Double-1>", self._on_double_click)
        self._tree.bind("<Button-1>", self._on_click_outside, add="+")
        self._entry_filter.bind("<Return>", self._on_filter_apply)

    def _reattach_all(self) -> None:
        if self._filter_applied:
            self._filter_applied = False
            for child, parent in self._tree_items:
                self._tree.reattach(child, parent, "end")  # type: ignore[arg-type]

    def _copy_item(self, item_id: str, column_id: str) -> None:
        if not item_id or not column_id:
            return None

        if column_id == "#0":
            value = self._tree.item(item_id, "text")
        else:
            column_index = int(column_id[1:]) - 1
            if not (column_values := self._tree.item(item_id, "values")):
                return None

            group, tag, value = column_values
            tag = f"{group}:{tag}"
            if column_index < 2:
                value = tag

        self.clipboard_clear()
        self.clipboard_append(value)

    def _on_expand_all(self) -> None:
        self._tree.expand_all()
        self._scrollable.scroll_to_top()
        self._scrollable.scroll_to_left()

    def _on_collapse_all(self) -> None:
        self._tree.collapse_all()
        self._scrollable.scroll_to_top()
        self._scrollable.scroll_to_left()

    def _on_double_click(self, event: tk.Event) -> None:
        self._copy_item(
            self._tree.identify_row(event.y), self._tree.identify_column(event.x)
        )

    def _on_click_outside(self, event: tk.Event) -> None:
        item = self._tree.identify_row(event.y)
        if not item:
            self._tree.selection_set(())

    def _on_clone(self):
        window = tk.Toplevel()
        window.title(f"{APP_NAME.capitalize()} - Metadata view")

        frame = MetadataView(window)
        frame.grid(
            column=0, row=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM
        )
        frame._button_clone.grid_remove()
        frame._label_filter.grid(row=1, column=2, sticky="e", padx=PADDING_SMALL)
        frame._entry_filter.grid(row=1, column=3, sticky="ew", padx=PADDING_SMALL)
        frame._button_filter_apply.grid(row=1, column=4, sticky="w", padx=PADDING_SMALL)
        frame._button_filter_clear.grid(
            row=1, column=5, sticky="w", padx=(PADDING_SMALL, 0)
        )
        frame.display_metadata(self._metadata or "")

        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.maxsize(
            self._tree.winfo_reqwidth() + PADDING_BIG,
            self._tree.winfo_reqheight() + PADDING_BIG,
        )
        window.minsize(*MIN_WIN_SIZE)
        window.geometry(f"{DEFAULT_WIN_SIZE[0]}x{DEFAULT_WIN_SIZE[1]}")

    def _on_filter_apply(self, event: tk.Event | None = None) -> None:
        self._scrollable.scroll_to_top()
        self._scrollable.scroll_to_left()
        text = self._pattern_var.get().strip()
        if not text:
            self._reattach_all()
            return None

        try:
            pattern = re.compile(text, re.IGNORECASE)
        except re.error:
            self._entry_filter.configure(style="Invalid.TEntry")
            return None

        self._entry_filter.configure(style="TEntry")

        def filter() -> None:
            for child, parent in self._tree_items:
                values = self._tree.item(child, "values")
                if not values:
                    self._tree.reattach(child, parent, "end")  # type: ignore[arg-type]
                else:
                    for value in values:
                        if pattern.search(value):
                            self._tree.reattach(
                                child,
                                parent,
                                "end",  # type: ignore[arg-type]
                            )
                            break
                    else:
                        self._tree.detach(child)

        self._tree.expand_all()
        filter()
        self._filter_applied = True

    def _on_filter_clear(self, event: tk.Event | None = None) -> None:
        self._scrollable.scroll_to_top()
        self._scrollable.scroll_to_left()
        self._pattern_var.set("")
        self._reattach_all()

    def display_metadata(self, metadata: str) -> None:
        self._metadata = metadata
        try:
            data = json.loads(metadata)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Couldn't parse ExifTool metadata report.")
            return None

        self._tree.delete(*self._tree.get_children())
        self._tree_items.clear()
        self._filter_applied = False

        self._scrollable.scroll_to_top()
        self._scrollable.scroll_to_left()
        total_items = 0

        for file_data in data:
            parent = self._tree.insert(
                "", "end", text=file_data["System:FileName"], open=False
            )
            self._tree_items.append((parent, ""))
            total_items += 1
            for key, value in file_data.items():
                group, *tag = key.split(":", maxsplit=1)
                child = self._tree.insert(
                    parent, "end", values=(group, tag, str(value).replace("\n", " | "))
                )
                self._tree_items.append((child, parent))
                total_items += 1

        self._tree.configure(height=total_items + 1)
