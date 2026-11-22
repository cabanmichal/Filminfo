import json
import platform
import re
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from filminfo.app.treeview import CustomTreeview
from filminfo.app.types import AnyWidget
from filminfo.configuration import (
    APP_NAME,
    DEFAULT_WIN_SIZE,
    MIN_WIN_SIZE,
    PADDING_MEDIUM,
    PADDING_SMALL,
)


_VALUE_MIN_WIDTH = 300
_VALUE_MAX_WIDTH = 2_000
_VALUE_PADDING = 20
_VALUES_TO_MEASURE = 50


class MetadataView(ttk.Frame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._metadata: str = "[]"
        self._tree_items: list[tuple[str, str]] = []
        self._filter_applied = False
        self._value_content_width = _VALUE_MIN_WIDTH

        # --- Elements ---
        self._tree_frame = ttk.Frame(self, width="10c", height="7c")
        self._tree_frame.grid_propagate(False)
        self._tree = CustomTreeview(
            self._tree_frame,
            columns=("group", "tag", "value"),
            selectmode="browse",
        )
        self._v_scroll = ttk.Scrollbar(
            self._tree_frame, orient="vertical", command=self._tree.yview
        )
        self._h_scroll = ttk.Scrollbar(
            self._tree_frame, orient="horizontal", command=self._tree.xview
        )
        self._tree.configure(
            yscrollcommand=self._v_scroll.set, xscrollcommand=self._h_scroll.set
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
        self._entry_filter = ttk.Entry(self, textvariable=self._pattern_var, width=12)
        self._button_filter_apply = ttk.Button(
            self, text="Apply", command=self._on_filter_apply
        )
        self._button_filter_clear = ttk.Button(
            self, text="Clear", command=self._on_filter_clear
        )

        self._button_clone = ttk.Button(self, text="New window", command=self._on_clone)

        self._layout()
        self.__configure()

    def _layout(self) -> None:
        self._label_data.grid(row=0, column=0, sticky="w")
        self._button_expand.grid(row=1, column=0, sticky="w")
        self._button_collapse.grid(row=1, column=1, sticky="w")
        self._entry_filter.grid(row=1, column=3, sticky="ew")
        self._button_clone.grid(row=1, column=6, sticky="e")

        self._tree_frame.grid(row=2, column=0, sticky="nsew", columnspan=7)
        self._tree.grid(row=0, column=0, sticky="nsew")
        self._v_scroll.grid(row=0, column=1, sticky="ns")
        self._h_scroll.grid(row=1, column=0, sticky="ew")
        self._tree_frame.rowconfigure(0, weight=1)
        self._tree_frame.columnconfigure(0, weight=1)

        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)

        for widget in [
            self._label_data,
            self._button_expand,
            self._button_collapse,
            self._entry_filter,
            self._button_clone,
            self._tree_frame,
        ]:
            widget.grid_configure(padx=PADDING_MEDIUM, pady=PADDING_SMALL)

    def __configure(self) -> None:
        self._tree.heading("#0", text="Filename")
        self._tree.heading("group", text="Group")
        self._tree.heading("tag", text="Tag name")
        self._tree.heading("value", text="Value", anchor="w")
        self._tree.column("#0", width=260, stretch=False)
        self._tree.column("group", width=100, stretch=False)
        self._tree.column("tag", width=200, stretch=False)
        self._tree.column("value", width=_VALUE_MIN_WIDTH, stretch=False)
        self._tree.bind("<Double-1>", self._on_double_click)
        self._tree.bind("<Button-1>", self._on_click_outside, add="+")
        self._tree.bind("<Configure>", lambda e: self._resize_value_column(), add="+")
        self._entry_filter.bind("<Return>", self._on_filter_apply)
        self._bind_horizontal_scroll()

    def _bind_horizontal_scroll(self) -> None:
        if platform.system() in ("Windows", "Darwin"):
            accumulator = 0.0

            def on_shift_wheel(event: tk.Event) -> str:
                nonlocal accumulator
                accumulator += -event.delta / 120
                if abs(accumulator) >= 1:
                    units = int(accumulator)
                    self._tree.xview_scroll(units, "units")
                    accumulator -= units
                return "break"

            self._tree.bind("<Shift-MouseWheel>", on_shift_wheel)
        else:
            self._tree.bind(
                "<Shift-Button-4>",
                lambda e: (self._tree.xview_scroll(-5, "units"), "break")[1],
            )
            self._tree.bind(
                "<Shift-Button-5>",
                lambda e: (self._tree.xview_scroll(5, "units"), "break")[1],
            )

    def _scroll_to_top_left(self) -> None:
        self._tree.yview_moveto(0)
        self._tree.xview_moveto(0)

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
        self._scroll_to_top_left()

    def _on_collapse_all(self) -> None:
        self._tree.collapse_all()
        self._scroll_to_top_left()

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
        frame._label_filter.grid(row=1, column=2, sticky="e")
        frame._button_filter_apply.grid(row=1, column=4, sticky="w")
        frame._button_filter_clear.grid(row=1, column=5, sticky="w")

        for widget in [
            frame._label_filter,
            frame._entry_filter,
            frame._button_filter_apply,
            frame._button_filter_clear,
        ]:
            widget.grid_configure(padx=PADDING_MEDIUM, pady=PADDING_SMALL)

        frame.display_metadata(self._metadata or "")

        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.minsize(*MIN_WIN_SIZE)
        window.geometry(f"{DEFAULT_WIN_SIZE[0]}x{DEFAULT_WIN_SIZE[1]}")

    def _on_filter_apply(self, event: tk.Event | None = None) -> None:
        self._scroll_to_top_left()
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
        self._scroll_to_top_left()
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

        self._scroll_to_top_left()

        values: list[str] = []
        for file_data in data:
            parent = self._tree.insert(
                "", "end", text=file_data["System:FileName"], open=False
            )
            self._tree_items.append((parent, ""))
            for key, value in file_data.items():
                group, *tag = key.split(":", maxsplit=1)
                text = str(value).replace("\n", " | ")
                values.append(text)
                child = self._tree.insert(parent, "end", values=(group, tag, text))
                self._tree_items.append((child, parent))

        self._fit_value_column(values)

    def _fit_value_column(self, values: list[str]) -> None:
        font_name = ttk.Style().lookup("Treeview", "font") or "TkDefaultFont"
        try:
            font = tkfont.nametofont(font_name)
        except tk.TclError:
            font = tkfont.Font(font=font_name)

        # Measuring every value is slow, so measure only the longest ones.
        longest = sorted(values, key=len, reverse=True)[:_VALUES_TO_MEASURE]
        text_width = max((font.measure(v) for v in longest), default=0)
        width = max(text_width + _VALUE_PADDING, _VALUE_MIN_WIDTH)
        self._value_content_width = min(width, _VALUE_MAX_WIDTH)
        self._resize_value_column()

    def _resize_value_column(self) -> None:
        other_columns = sum(
            int(self._tree.column(col, "width")) for col in ("#0", "group", "tag")
        )
        spare = self._tree.winfo_width() - other_columns
        width = max(self._value_content_width, spare)
        if int(self._tree.column("value", "width")) != width:
            self._tree.column("value", width=width)
