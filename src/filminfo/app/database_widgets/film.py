import tkinter as tk
from tkinter import messagebox, ttk

from filminfo.app.combobox import ShiftScrollCombobox
from filminfo.app.database_widgets import save_database
from filminfo.app.types import AnyWidget
from filminfo.configuration import PADDING_SMALL
from filminfo.controllers.database_controller import DatabaseController
from filminfo.models.entities import Film, FilmFormat
from filminfo.models.validators import iso_valid


class FilmWidget(ttk.LabelFrame):
    def __init__(
        self, parent: AnyWidget, controller: DatabaseController, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self._controller = controller
        self._films = self._controller.get_films()

        # --- Variables ---
        self._film_var = tk.StringVar()
        self._make_var = tk.StringVar()
        self._name_var = tk.StringVar()
        self._iso_var = tk.StringVar()
        self._format_var = tk.StringVar(value=FilmFormat.FILM_135.value)

        # --- Film selection ---
        self._label_film = ttk.Label(self, text="Saved:")
        self._combo_film = ShiftScrollCombobox(
            self,
            textvariable=self._film_var,
            values=self._get_film_names(),
            state="readonly",
        )
        self._combo_film.bind("<<ComboboxSelected>>", self._on_combo_select)
        self._button_remove = ttk.Button(self, text="Remove", command=self._on_remove)

        # --- Make ---
        self._label_make = ttk.Label(self, text="Make:")
        self._entry_make = ttk.Entry(self, textvariable=self._make_var)

        # --- Name ---
        self._label_name = ttk.Label(self, text="Name:")
        self._entry_name = ttk.Entry(self, textvariable=self._name_var)

        # --- ISO ---
        self._label_iso = ttk.Label(self, text="ISO:")
        self._entry_iso = ttk.Entry(
            self,
            textvariable=self._iso_var,
            validate="key",
            validatecommand=(self.register(iso_valid), "%P"),
        )

        # --- Format ---
        self._label_format = ttk.Label(self, text="Format:")
        self._combo_format = ShiftScrollCombobox(
            self,
            textvariable=self._format_var,
            values=[fmt.value for fmt in FilmFormat],
        )

        # --- Buttons ---
        self._button_clear = ttk.Button(self, text="Clear", command=self._on_clear)
        self._button_add = ttk.Button(self, text="Add", command=self._on_add)

        self._layout()

    def _layout(self) -> None:
        # --- Film selection ---
        self._label_film.grid(row=0, column=0, sticky="w")
        self._combo_film.grid(row=0, column=1, sticky="ew")
        self._button_remove.grid(row=0, column=2, padx=PADDING_SMALL)

        # --- Make ---
        self._label_make.grid(row=1, column=0, sticky="w")
        self._entry_make.grid(row=1, column=1, columnspan=2, sticky="ew")

        # --- Name ---
        self._label_name.grid(row=2, column=0, sticky="w")
        self._entry_name.grid(row=2, column=1, columnspan=2, sticky="ew")

        # --- ISO ---
        self._label_iso.grid(row=3, column=0, sticky="w")
        self._entry_iso.grid(row=3, column=1, columnspan=2, sticky="ew")

        # --- Format ---
        self._label_format.grid(row=4, column=0, sticky="w")
        self._combo_format.grid(row=4, column=1, columnspan=2, sticky="ew")

        # --- buttons ---
        self._button_clear.grid(row=5, column=0, sticky="w", padx=PADDING_SMALL)
        self._button_add.grid(row=5, column=2, sticky="e", padx=PADDING_SMALL)

        self.columnconfigure(1, weight=1)

    def _make_film_name(self, film: Film) -> str:
        return f"{film.make} {film.name}"

    def _get_film_names(self) -> list[str]:
        return [self._make_film_name(film) for film in self._controller.get_films()]

    def _get_film(self) -> Film | None:
        index = self._combo_film.current()
        if index >= 0 and index < len(self._films):
            return self._films[index]

        return None

    # --- Callbacks ---
    def _on_combo_select(self, event: tk.Event | None = None) -> None:
        film = self._get_film()
        if film:
            self._make_var.set(film.make)
            self._name_var.set(film.name)
            self._iso_var.set(str(film.iso))

    def _on_remove(self) -> None:
        film = self._get_film()
        if film:
            self._controller.remove_film(film)
            save_database(self._controller)
            self._films = self._controller.get_films()
            self._combo_film["values"] = self._get_film_names()

        self._film_var.set("")

    def _on_add(self) -> None:
        make = self.make
        name = self.name
        iso = self.iso

        if not make or not name:
            messagebox.showerror("Error", "Make and Name cannot be empty.")
            return

        if not iso_valid(iso):
            messagebox.showerror("Error", "ISO must be a positive integer.")
            return

        film = Film(make, name, int(iso))
        self._controller.add_film(film)
        save_database(self._controller)
        self._films = self._controller.get_films()
        self._combo_film["values"] = self._get_film_names()
        self._film_var.set(self._make_film_name(film))

    def _on_clear(self) -> None:
        self.clear()

    # --- Public methods ---
    @property
    def film(self) -> str:
        return self._film_var.get().strip()

    @property
    def make(self) -> str:
        return self._make_var.get().strip()

    @property
    def name(self) -> str:
        return self._name_var.get().strip()

    @property
    def iso(self) -> str:
        return self._iso_var.get().strip()

    @property
    def format(self) -> str:
        return self._format_var.get().strip()

    def clear(self) -> None:
        self._film_var.set("")
        self._make_var.set("")
        self._name_var.set("")
        self._iso_var.set("")
        self._format_var.set("")
