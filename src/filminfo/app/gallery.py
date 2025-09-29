import platform
import re
import tkinter as tk
from collections.abc import Iterable, Sequence
from tkinter import filedialog, ttk

from filminfo.app import add_bindtag, find_ancestor
from filminfo.app.scrollable_frame import ScrollableFrame
from filminfo.app.thumbnail import Thumbnail
from filminfo.app.types import AnyWidget
from filminfo.configuration import PADDING_SMALL


class Gallery(ttk.Frame):
    TAG = "Gallery"

    def __init__(
        self,
        parent: AnyWidget,
        thumbnail_size: int,
        preview_size: int,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, takefocus=True, **kwargs)
        self._thumbnail_size = thumbnail_size
        self._preview_size = preview_size
        self._thumbnails: list[Thumbnail] = []
        self._selected = 0
        self._columns = 0

        self._toolbar = _Toolbar(self)
        self._statusbar = _StatusBar(self)
        self._scrollable = ScrollableFrame(self, horizontal=False)
        self._container = self._scrollable.container

        self._layout()
        self.__configure()

    def _layout(self) -> None:
        self._toolbar.grid(row=0, column=0, sticky="ew")
        self._scrollable.grid(row=1, column=0, sticky="nsew")
        self._statusbar.grid(row=2, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def __configure(self) -> None:
        for widget in [
            self,
            self._scrollable.container,
            self._scrollable.canvas,
        ]:
            add_bindtag(widget, Gallery.TAG)

        control_key = "Command" if platform.system() == "Darwin" else "Control"
        delete_key = "BackSpace" if platform.system() == "Darwin" else "Delete"
        self.bind("<Configure>", self._on_resize)
        self.bind("<Escape>", self._on_deselect_all)
        self.bind(f"<{control_key}-a>", self._on_select_all)
        self.bind("<asterisk>", self._on_invert_selection)
        self.bind(f"<{delete_key}>", self._on_remove_images)
        self.bind_all(f"<{control_key}-o>", self._on_add_images)

        self.bind_class(Gallery.TAG, "<Button-1>", self._on_gallery_click, add="+")
        self.bind_class(Thumbnail.TAG, "<Button-1>", self._on_thumbnail_left_click)
        self.bind_class(Thumbnail.TAG, "<Button-3>", self._on_thumbnail_right_click)

        self._toolbar.button_add.configure(command=self._on_add_images)
        self._toolbar.button_pattern_apply.configure(command=self._on_pattern_apply)
        self._toolbar.entry_pattern.bind("<Return>", self._on_pattern_apply)

    def _draw_thumbnails(self, columns: int, sort: bool = False) -> None:
        if not self._thumbnails:
            return

        for thumbnail in self._thumbnails:
            thumbnail.grid_remove()

        thumbnails = (
            sorted(self._thumbnails, key=lambda t: t.file_path)
            if sort
            else self._thumbnails
        )
        for idx, thumbnail in enumerate(thumbnails):
            row, column = divmod(idx, columns)
            thumbnail.grid(
                row=row,
                column=column,
                padx=PADDING_SMALL,
                pady=PADDING_SMALL,
                sticky="n",
            )
        self._columns = columns

    def _load_thumbnails(self, images: Iterable[str]) -> None:
        thumbnails = []
        for image in images:
            thumbnails.append(
                Thumbnail(
                    self._container,
                    image,
                    size=self._thumbnail_size,
                    preview_size=self._preview_size,
                )
            )
        thumbnails.sort(key=lambda t: t.file_path)
        self._thumbnails.extend(thumbnails)

    def _get_images(self) -> Iterable[str]:
        images = filedialog.askopenfilenames(
            title="Select an images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tif *.tiff"),
                ("All files", "*.*"),
            ],
        )

        in_gallery = set(self.all_images)

        return [image for image in images if image not in in_gallery]

    def _update_status_bar(self) -> None:
        self._statusbar.set_image_counts(
            len(self.selected_images), len(self._thumbnails)
        )

    def _get_number_of_columns(self) -> int:
        self.update_idletasks()
        thumbnail_width = self._get_thumbnail_size()
        if thumbnail_width:
            columns = max(
                1,
                self._container.winfo_width() // (thumbnail_width + 2 * PADDING_SMALL),
            )
            return columns
        return 0

    def _get_thumbnail_size(self) -> int:
        if self._thumbnails:
            return self._thumbnails[0].winfo_reqwidth()
        return 0

    def _on_thumbnail_left_click(self, event: tk.Event) -> None:
        thumbnail = find_ancestor(event.widget, Thumbnail)
        if thumbnail:
            thumbnail.toggle()
            self._update_status_bar()
        self.focus_set()

    def _on_thumbnail_right_click(self, event: tk.Event) -> None:
        thumbnail = find_ancestor(event.widget, Thumbnail)
        if thumbnail:
            thumbnail.show_preview()
        self.focus_set()

    def _on_gallery_click(self, event: tk.Event) -> None:
        self._on_deselect_all()
        self.focus_set()

    def _on_add_images(self, event: tk.Event | None = None) -> None:
        images = self._get_images()
        if images:
            self._load_thumbnails(images)
            self._draw_thumbnails(self._get_number_of_columns())
        self._update_status_bar()
        self.focus_set()

    def _on_remove_images(self, event: tk.Event | None = None) -> None:
        selected = [thumbnail for thumbnail in self._thumbnails if thumbnail.selected]
        self._thumbnails = [
            thumbnail for thumbnail in self._thumbnails if not thumbnail.selected
        ]

        for thumbnail in selected:
            thumbnail.destroy()

        self._draw_thumbnails(self._get_number_of_columns())
        self._update_status_bar()
        self.focus_set()

    def _on_select_all(self, event: tk.Event | None = None) -> None:
        if self._thumbnails:
            self.select_all()
            self._update_status_bar()

    def _on_deselect_all(self, event: tk.Event | None = None) -> None:
        if self._thumbnails:
            self.deselect_all()
            self._update_status_bar()

    def _on_invert_selection(self, event: tk.Event | None = None) -> None:
        for thumbnail in self._thumbnails:
            thumbnail.toggle()
        self._update_status_bar()

    def _on_resize(self, event: tk.Event) -> None:
        if (columns := self._get_number_of_columns()) != self._columns:
            self._draw_thumbnails(columns)
        self.focus_set()

    def _on_pattern_apply(self, event: tk.Event | None = None) -> None:
        self._scrollable.scroll_to_top()
        self._scrollable.scroll_to_left()
        self.focus_set()

        text = self._toolbar.pattern
        if not text:
            self.deselect_all()
            return

        try:
            pattern = re.compile(text)
        except re.error:
            self._toolbar.entry_pattern.configure(style="Invalid.TEntry")
            return None

        self._toolbar.entry_pattern.configure(style="TEntry")
        self.deselect_all()
        for thumbnail in self._thumbnails:
            if pattern.search(thumbnail.file_path):
                thumbnail.select()
        self._update_status_bar()

    def deselect_all(self) -> None:
        for thumbnail in self._thumbnails:
            thumbnail.deselect()

    def select_all(self) -> None:
        for thumbnail in self._thumbnails:
            thumbnail.select()

    @property
    def all_images(self) -> Sequence[str]:
        return [t.file_path for t in self._thumbnails]

    @property
    def selected_images(self) -> Sequence[str]:
        return [t.file_path for t in self._thumbnails if t.selected]


class _Toolbar(ttk.Frame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.button_add = ttk.Button(self, text="Add images")
        self._pattern_var = tk.StringVar()
        self._label_pattern = ttk.Label(self, text="Select by regex:")
        self.entry_pattern = ttk.Entry(self, textvariable=self._pattern_var)
        self.button_pattern_apply = ttk.Button(self, text="Apply")

        self._layout()

    def _layout(self) -> None:
        self.button_add.grid(row=0, column=0, sticky="w", padx=(0, PADDING_SMALL))
        self._label_pattern.grid(row=0, column=1, sticky="e", padx=(0, PADDING_SMALL))
        self.entry_pattern.grid(row=0, column=2, sticky="ew")
        self.button_pattern_apply.grid(row=0, column=3, sticky="w", padx=PADDING_SMALL)

    @property
    def pattern(self) -> str:
        return self._pattern_var.get().strip()


class _StatusBar(ttk.Frame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._label_var = tk.StringVar()
        self._label = ttk.Label(self, textvariable=self._label_var)
        self._label.grid(row=0, column=0, sticky="e")
        self.columnconfigure(0, weight=1)

    def set_image_counts(self, selected: int, total: int) -> None:
        self._label_var.set(f"Selected: {selected}/{total}")
