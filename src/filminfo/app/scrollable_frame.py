import platform
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from filminfo.app.types import AnyWidget


_CALLBACK = Callable[[tk.Event], None]


class ScrollableFrame(ttk.Frame):
    def __init__(
        self,
        parent: AnyWidget,
        *args,
        vertical: bool = True,
        horizontal: bool = True,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self._canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self._v_scroll = ttk.Scrollbar(self, orient="vertical")
        self._h_scroll = ttk.Scrollbar(self, orient="horizontal")
        self._container = ttk.Frame(self._canvas, borderwidth=0)
        self._container_id = self._canvas.create_window(
            (0, 0), window=self._container, anchor="nw"
        )
        self._vertical_enabled = vertical
        self._horizontal_enabled = horizontal
        self._on_scroll = self._mouse_callback()

        self._layout()
        self.__configure()

    def _layout(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._v_scroll.grid(row=0, column=1, sticky="ns")
        self._h_scroll.grid(row=1, column=0, sticky="ew")

    def __configure(self) -> None:
        self._canvas.configure(
            yscrollcommand=self._v_scroll.set,
            xscrollcommand=self._h_scroll.set,
        )
        self._v_scroll.configure(command=self._canvas.yview)
        self._h_scroll.configure(command=self._canvas.xview)

        self._container.bind("<Configure>", self._on_container_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self._canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _bind_mousewheel(self) -> None:
        for button in ["<MouseWheel>", "<Button-4>", "<Button-5>"]:
            self._canvas.bind_all(button, self._on_scroll)

    def _unbind_mousewheel(self) -> None:
        for button in ["<MouseWheel>", "<Button-4>", "<Button-5>"]:
            self._canvas.unbind_all(button)

    def _on_container_configure(self, event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox(self._container_id))
        self._toggle_scrollbars()

    def _on_canvas_configure(self, event: tk.Event) -> None:
        if self._horizontal_enabled:
            self._canvas.itemconfig(
                self._container_id, width=self._container.winfo_reqwidth()
            )
        else:
            self._canvas.itemconfig(self._container_id, width=event.width)

    def _toggle_scrollbars(self) -> None:
        scrollregion_width, scollregion_height = self._content_dimensions()
        canvas_width, canvas_height = self._canvas_dimensions()

        if self._vertical_enabled and scollregion_height > canvas_height:
            self._v_scroll.grid()
        else:
            self._v_scroll.grid_remove()

        if self._horizontal_enabled and scrollregion_width > canvas_width:
            self._h_scroll.grid()
        else:
            self._h_scroll.grid_remove()

    def _content_dimensions(self) -> tuple[int, int]:
        x0, y0, x1, y1 = self._canvas.bbox("all") or (0, 0, 0, 0)
        return x1 - x0, y1 - y0

    def _canvas_dimensions(self) -> tuple[int, int]:
        return self._canvas.winfo_width(), self._canvas.winfo_height()

    def _mouse_callback(self) -> _CALLBACK:
        system = platform.system()
        if system == "Windows" or system == "Darwin":
            accumulator = 0.0

            def callback(event: tk.Event) -> None:
                nonlocal accumulator
                accumulator += -event.delta / 120

                if abs(accumulator) >= 1:
                    units = int(accumulator)
                    scroll = True
                    scrollregion_width, scollregion_height = self._content_dimensions()
                    canvas_width, canvas_height = self._canvas_dimensions()

                    if (
                        int(event.state) & 0x0001
                        and self._horizontal_enabled
                        and scrollregion_width > canvas_width
                    ):
                        self._canvas.xview_scroll(units, "units")
                    elif self._vertical_enabled and scollregion_height > canvas_height:
                        self._canvas.yview_scroll(units, "units")
                    else:
                        scroll = False

                    if scroll:
                        accumulator -= units

        else:

            def callback(event: tk.Event) -> None:
                scrollregion_width, scollregion_height = self._content_dimensions()
                canvas_width, canvas_height = self._canvas_dimensions()

                if (
                    int(event.state) & 0x0001
                    and self._horizontal_enabled
                    and scrollregion_width > canvas_width
                ):
                    if event.num == 4:
                        self._canvas.xview_scroll(-1, "units")
                    elif event.num == 5:
                        self._canvas.xview_scroll(1, "units")
                elif self._vertical_enabled and scollregion_height > canvas_height:
                    if event.num == 4:
                        self._canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        self._canvas.yview_scroll(1, "units")

        return callback

    @property
    def container(self) -> ttk.Frame:
        return self._container

    @property
    def canvas(self) -> tk.Canvas:
        return self._canvas

    def scroll_to_top(self) -> None:
        self._canvas.yview_moveto(0)

    def scroll_to_left(self) -> None:
        self._canvas.xview_moveto(0)
