import os
import tkinter as tk
from collections.abc import Callable

from PIL import Image, ImageTk

from filminfo.app import add_bindtag
from filminfo.app.types import AnyWidget
from filminfo.configuration import PADDING_SMALL, get_string_option

ThumbnailCallback = Callable[["Thumbnail"], None]


class Thumbnail(tk.Frame):
    TAG = "Thumbnail"

    def __init__(
        self,
        parent: AnyWidget,
        image_path: str,
        size: int,
        preview_size: int,
        **kwargs,
    ):
        super().__init__(parent, width=size, height=size, **kwargs)
        self._image_path = image_path
        self._image_name = os.path.basename(image_path)
        self._size = size
        self._highlightthickness = 3
        self._highlight_color = (
            get_string_option("thumbnail_highlight_color") or "SystemHighlight"
        )
        self._label_height = 40  # kind of works on my macbook air
        self._padx = PADDING_SMALL
        self._pady = PADDING_SMALL
        self._preview_size = preview_size
        self._preview: ImageTk.PhotoImage | None = None
        self._selected = False
        self._click_job: str | None = None

        self._create_widgets()
        self._layout()
        self.__configure()

    def _create_widgets(self) -> None:
        width = self._size - 2 * self._padx - 2 * self._highlightthickness
        photo = self._create_photo_image(width, width - self._label_height)
        self._image_label = tk.Label(self, image=photo)
        self._default_highlight_color = self.cget("highlightbackground")
        self._thumbnail: ImageTk.PhotoImage = photo
        self._name_label = tk.Label(
            self,
            text=self._process_label_text(),
            wraplength=self._size - 2 * self._padx - 2 * self._highlightthickness,
            anchor="center",
        )

    def _layout(self) -> None:
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._image_label.grid(row=0, column=0, sticky="nsew")
        self._name_label.grid(row=1, column=0, sticky="new")

    def __configure(self) -> None:
        self.configure(highlightthickness=self._highlightthickness)
        for widget in [self, self._image_label, self._name_label]:
            add_bindtag(widget, Thumbnail.TAG)

    def _create_photo_image(self, width: int, height) -> ImageTk.PhotoImage:
        image = Image.open(self._image_path)
        if image.width > width or image.height > height:
            size = height if image.width < image.height else width
            image.thumbnail((size, size))

        return ImageTk.PhotoImage(image)

    def _process_label_text(self) -> str:
        limit = 36  # seems to fit OK in self._label_height
        name, ext = os.path.splitext(self._image_name)
        if len(name) + len(ext) > limit:
            limit -= len(ext) + 3  # for ...
            left = name[: limit // 2]
            right = name[-limit // 2 :]
            return left + "..." + right + ext
        return self._image_name

    def _select(self) -> None:
        self._selected = True
        self.configure(highlightbackground=self._highlight_color)

    def _deselect(self) -> None:
        self._selected = False
        self.configure(highlightbackground=self._default_highlight_color)

    # --- Public methods ---
    @property
    def file_path(self) -> str:
        return self._image_path

    @property
    def image_name(self) -> str:
        return self._image_name

    @property
    def selected(self) -> bool:
        return self._selected

    def select(self) -> None:
        self._select()

    def deselect(self) -> None:
        self._deselect()

    def toggle(self) -> None:
        self.deselect() if self.selected else self.select()

    def show_preview(self) -> None:
        if self._preview:
            return

        window = tk.Toplevel()
        window.title(self._image_path)
        photo = self._create_photo_image(self._preview_size, self._preview_size)
        label = tk.Label(window, image=photo)
        self._preview = photo
        label.grid()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        def on_preview_close():
            self._preview = None
            window.destroy()

        label.bind("<Button-3>", lambda e: on_preview_close())
        window.protocol("WM_DELETE_WINDOW", on_preview_close)
