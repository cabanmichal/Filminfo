import os
import platform
import subprocess
import tkinter as tk
from collections.abc import Callable, Sequence
from tkinter import messagebox, ttk

from filminfo.app.form_add import AddMetadataForm as FormAdd
from filminfo.app.form_remove import RemoveMetadaForm as FormRemove
from filminfo.app.gallery import Gallery
from filminfo.app.metadata_view import MetadataView
from filminfo.app.notebook import ShiftScrollNotebook
from filminfo.app.types import AnyWidget
from filminfo.configuration import (
    APP_NAME,
    DEFAULT_WIN_SIZE,
    MIN_WIN_SIZE,
    PADDING_BIG,
    ensure_database,
    get_app_dir,
    get_exiftool,
    get_int_option,
    get_string_option,
    load_config,
)
from filminfo.controllers.database_controller import DatabaseController
from filminfo.controllers.exiftool_controller import ExifToolController
from filminfo.models.exiftool import ExifToolReply


class App(ttk.Frame):
    def __init__(
        self,
        parent: AnyWidget,
        thumbnail_size: int,
        preview_size: int,
        database_controller: DatabaseController,
        exiftool_controller: ExifToolController,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self._exiftool_controller = exiftool_controller

        self._gallery = Gallery(
            self, thumbnail_size=thumbnail_size, preview_size=preview_size
        )
        self._notebook = ShiftScrollNotebook(self)
        self._form_add_metadata = FormAdd(self._notebook, database_controller)
        self._form_remove_metadata = FormRemove(self._notebook)
        self._metadata_view = MetadataView(self._notebook)
        self._separator = ttk.Separator(self)
        self._button_open_dir = ttk.Button(
            self, text="Application folder", command=self._on_folder_open
        )
        self._button_execute = ttk.Button(self, text="Execute")

        self._layout()
        self.__configure()

    def _layout(self) -> None:
        self._gallery.grid(row=0, column=0, sticky="nsew", padx=(PADDING_BIG, 0))
        self._notebook.grid(row=0, column=1, sticky="nsew")
        self._separator.grid(row=1, column=0, columnspan=2, sticky="we")
        self._button_open_dir.grid(
            row=2, column=0, sticky="w", padx=PADDING_BIG, pady=PADDING_BIG
        )
        self._button_execute.grid(
            row=2, column=1, sticky="e", padx=PADDING_BIG, pady=PADDING_BIG
        )

        self.columnconfigure(0, weight=1, minsize=500)
        self.columnconfigure(1, weight=0, minsize=530)
        self.rowconfigure(0, weight=1)

    def __configure(self) -> None:
        self._notebook.add(self._form_add_metadata, text="Add metadata")
        self._notebook.add(self._form_remove_metadata, text="Remove metadata")
        self._notebook.add(self._metadata_view, text="View metadata")
        self._notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _add_metadata(self) -> None:
        if not messagebox.askyesno(
            "Confirm", "Are you sure you want to add metadata to selected images?"
        ):
            return None

        self._call_exiftool(
            lambda: self._exiftool_controller.add_metadata(
                images=self.selected_images, metadata=self.form_data
            )
        )

    def _remove_metadata(self) -> None:
        if not messagebox.askyesno(
            "Confirm", "Are you sure you want to remove metadata from selected images?"
        ):
            return None

        self._call_exiftool(
            lambda: self._exiftool_controller.remove_metadata(
                images=self.selected_images, tags=self.tags_to_remove
            )
        )

    def _display_metadata(self) -> None:
        error, data = self._call_exiftool(
            lambda: self._exiftool_controller.get_metadata(images=self.selected_images),
            showmessage=False,
        )

        if not error:
            self._metadata_view.display_metadata(data)

    def _call_exiftool(
        self, action: Callable[[], ExifToolReply], showmessage: bool = True
    ) -> ExifToolReply:
        self._button_execute.configure(state="disabled")

        reply = action()
        error, message = reply
        if error:
            messagebox.showerror("ExifTool Error", str(error), icon="error")
        elif message:
            if showmessage:
                messagebox.showinfo("ExifTool Info", message, icon="info")
        else:
            messagebox.showwarning(
                f"{APP_NAME.capitalize()} Warning",
                "This shouldn't have happened",
                icon="warning",
            )

        self._button_execute.configure(state="!disabled")

        return reply

    # --- Callbacks ---
    def _on_tab_change(self, event: tk.Event) -> None:
        tab_id = self._notebook.select()
        tab_index = self._notebook.index(tab_id)

        if tab_index == 0:
            callback = self._add_metadata
        elif tab_index == 1:
            callback = self._remove_metadata
        else:
            callback = self._display_metadata
            self._button_execute.focus_set()

        self._button_execute.configure(command=callback)

    def _on_folder_open(self) -> None:
        system = platform.system()
        folder = get_app_dir()
        if system == "Windows":
            os.startfile(folder)  # type: ignore
        elif system == "Darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])

    # --- Public methods ---
    @property
    def selected_images(self) -> Sequence[str]:
        return self._gallery.selected_images

    @property
    def form_data(self) -> dict[str, str]:
        return self._form_add_metadata.form_data

    @property
    def tags_to_remove(self) -> Sequence[str]:
        return self._form_remove_metadata.selected_items


def main():
    root = tk.Tk()
    root.title(APP_NAME.capitalize())

    try:
        database_file = ensure_database()
        database_controller = DatabaseController(database_file)
        load_config()
    except Exception as err:
        messagebox.showerror("Error", str(err))
        root.destroy()

    style = ttk.Style(root)
    if theme := get_string_option("theme"):
        style.theme_use(str(theme))
    error_text_color = get_string_option("error_text_color")
    style.configure("Invalid.TEntry", foreground=error_text_color)
    style.configure("Invalid.TCombobox", foreground=error_text_color)
    tree_highlight_color = get_string_option("tree_highlight_color")
    style.map("Treeview", background=[("selected", tree_highlight_color)])

    app = App(
        root,
        thumbnail_size=get_int_option("thumbnail_size"),
        preview_size=get_int_option("preview_size"),
        database_controller=database_controller,
        exiftool_controller=ExifToolController(get_exiftool()),
    )
    app.grid(row=0, column=0, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.minsize(*MIN_WIN_SIZE)
    root.geometry(f"{DEFAULT_WIN_SIZE[0]}x{DEFAULT_WIN_SIZE[1]}")

    root.mainloop()
