import tkinter as tk
from enum import Enum
from pathlib import Path
from tkinter import filedialog, ttk

from filminfo.app.types import AnyWidget
from filminfo.configuration import PADDING_MEDIUM, PADDING_SMALL


class Choice(Enum):
    EXPORT = "export"
    IMPORT = "import"


class MetadaExportImport(ttk.Frame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._choice_var = tk.StringVar(value=Choice.EXPORT.value)
        self._choice_export = ttk.Radiobutton(
            self, text="Export", variable=self._choice_var, value=Choice.EXPORT.value
        )
        self._choice_import = ttk.Radiobutton(
            self, text="Import", variable=self._choice_var, value=Choice.IMPORT.value
        )
        self._path_var = tk.StringVar()
        self._path_entry = ttk.Entry(self, textvariable=self._path_var)
        self._path_button = ttk.Button(
            self, text="Select json", command=self._browse_file
        )

        self._layout()

    def _browse_file(self) -> None:
        title = "Select a JSON file"
        defaultextension = ".json"
        filetypes = [("JSON files", "*.json")]

        if self._choice_var.get() == Choice.EXPORT.value:
            filepath = filedialog.asksaveasfilename(
                title=title,
                defaultextension=defaultextension,
                filetypes=filetypes,
                initialfile="metadata.json",
            )
        else:
            filepath = filedialog.askopenfilename(
                title=title, defaultextension=defaultextension, filetypes=filetypes
            )

        if filepath:
            self._path_var.set(filepath)

    def _layout(self) -> None:
        self._choice_export.grid(row=0, column=0, sticky="w")
        self._choice_import.grid(row=1, column=0, sticky="w")
        self._path_entry.grid(row=2, column=0, sticky="ew")
        self._path_button.grid(row=2, column=1, sticky="w")

        self.columnconfigure(0, weight=1)

        for widget in self.winfo_children():
            widget.grid_configure(padx=PADDING_MEDIUM, pady=PADDING_SMALL)

    @property
    def choice(self) -> Choice:
        return Choice(self._choice_var.get())

    @property
    def path(self) -> Path | None:
        filepath = self._path_var.get()
        if filepath:
            return Path(filepath)

        return None
