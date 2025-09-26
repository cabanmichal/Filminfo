import tkinter as tk
from tkinter import ttk

from filminfo.app.types import AnyWidget, ButtonCallback
from filminfo.app.validating_entry import ValidatingEntry
from filminfo.configuration import PADDING_SMALL
from filminfo.models.validators import aperture_valid, iso_valid, shutter_speed_valid


class ExposureWidget(ttk.LabelFrame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # --- Variables ---
        self._aperture_var = tk.StringVar()
        self._ss_var = tk.StringVar()
        self._iso_var = tk.StringVar()

        # --- Elements ---
        self._label_aperture = ttk.Label(self, text="Aperture:")
        self._entry_aperture = ValidatingEntry(self, textvariable=self._aperture_var)
        self._entry_aperture.set_command(
            lambda aperture: not aperture or aperture_valid(str(aperture))
        )

        self._label_ss = ttk.Label(self, text="Shutter speed:")
        self._entry_ss = ValidatingEntry(self, textvariable=self._ss_var)
        self._entry_ss.set_command(
            lambda sspeed: not sspeed or shutter_speed_valid(str(sspeed))
        )

        self._label_iso = ttk.Label(self, text="ISO:")
        self._entry_iso = ValidatingEntry(self, textvariable=self._iso_var)
        self._entry_iso.set_command(lambda iso: not iso or iso_valid(str(iso)))
        self._button_as_film = ttk.Button(self, text="As film")

        self._button_clear = ttk.Button(self, text="Clear", command=self._on_clear)

        self._layout()

    def _layout(self) -> None:
        # --- Aperture ---
        self._label_aperture.grid(row=0, column=0, sticky="w")
        self._entry_aperture.grid(row=0, column=1, columnspan=2, sticky="ew")

        # --- Shutter speed ---
        self._label_ss.grid(row=1, column=0, sticky="w")
        self._entry_ss.grid(row=1, column=1, columnspan=2, sticky="ew")

        # --- ISO ---
        self._label_iso.grid(row=2, column=0, sticky="w")
        self._entry_iso.grid(row=2, column=1, sticky="ew")
        self._button_as_film.grid(row=2, column=2, sticky="w", padx=PADDING_SMALL)

        # --- buttons ---
        self._button_clear.grid(row=6, column=0, sticky="w", padx=PADDING_SMALL)

        self.columnconfigure(1, weight=1)

    # --- Callbacks ---
    def _on_clear(self) -> None:
        self.clear()

    # --- Public methods ---
    @property
    def aperture(self) -> str:
        return self._aperture_var.get().strip()

    @property
    def shutter_speed(self) -> str:
        return self._ss_var.get().strip()

    @property
    def iso(self) -> str:
        return self._iso_var.get().strip()

    @iso.setter
    def iso(self, value: str) -> None:
        self._iso_var.set(value)

    def set_as_film_command(self, command: ButtonCallback) -> None:
        self._button_as_film.config(command=command)

    def clear(self) -> None:
        self._aperture_var.set("")
        self._ss_var.set("")
        self._iso_var.set("")
