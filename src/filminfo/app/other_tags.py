import tkinter as tk
from tkinter import ttk

from filminfo.app.types import AnyWidget
from filminfo.app.validating_entry import ValidatingEntry
from filminfo.configuration import PADDING_MEDIUM, PADDING_SMALL
from filminfo.models.validators import resolution_valid


class OtherTags(ttk.LabelFrame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # --- Elements ---
        self._label_resolution = ttk.Label(self, text="Resolution:")
        self._resolution_var = tk.StringVar()
        self._entry_resolution = ValidatingEntry(
            self, textvariable=self._resolution_var
        )
        self._entry_resolution.set_command(
            lambda resolution: not resolution or resolution_valid(str(resolution))
        )

        self._label_other_tags = ttk.Label(
            self,
            text=(
                "Other (comma separated):\n"
                "Example: -EXIF:Software=Adobe Photoshop, -EXIF:Orientation#=6"
            ),
        )
        self._text_other_tags = tk.Text(self, height=5, width=50)

        self._button_clear = ttk.Button(self, text="Clear", command=self._on_clear)

        self._layout()

    def _layout(self) -> None:
        # --- Resolution ---
        self._label_resolution.grid(row=0, column=0, sticky="w")
        self._entry_resolution.grid(row=0, column=1, sticky="ew")

        # --- Other tags ---
        self._label_other_tags.grid(row=2, column=0, columnspan=2, sticky="w")
        self._text_other_tags.grid(row=3, column=0, columnspan=2, sticky="ew")

        # --- Buttons ---
        self._button_clear.grid(row=4, column=0, sticky="w")

        self.columnconfigure(1, weight=1)

        for widget in self.winfo_children():
            widget.grid_configure(padx=PADDING_MEDIUM, pady=PADDING_SMALL)

    # --- Callbacks ---
    def _on_clear(self) -> None:
        self.clear()

    # --- Public methods ---
    @property
    def resolution(self) -> str:
        return self._entry_resolution.get().strip()

    @property
    def other_tags(self) -> list[str]:
        tags = self._text_other_tags.get("1.0", "end").strip().split(",")
        return [tag.strip() for tag in tags]

    @property
    def data(self) -> dict[str, str]:
        return {
            "other_resolution": self.resolution,
            "other_tags": ",".join(self.other_tags),
        }

    def clear(self) -> None:
        self._resolution_var.set("")
        self._text_other_tags.delete("1.0", "end")
