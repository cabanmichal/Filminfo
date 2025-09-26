import tkinter as tk
from datetime import datetime, time
from tkinter import ttk

from filminfo.app.combobox import ShiftScrollCombobox
from filminfo.app.types import AnyWidget
from filminfo.app.validating_entry import ValidatingEntry
from filminfo.configuration import PADDING_SMALL, get_string_option
from filminfo.models.entities import COUNTRIES
from filminfo.models.validators import date_taken_valid


class OriginWidget(ttk.LabelFrame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # --- Variables ---
        self._author_var = tk.StringVar(value=get_string_option("author"))
        self._copyright_var = tk.StringVar()
        self._city_var = tk.StringVar()
        self._country_var = tk.StringVar(value=self._get_default_country())
        self._sublocation_var = tk.StringVar()
        self._date_taken_var = tk.StringVar(value=_default_time())

        # --- Elements ---
        self._label_author = ttk.Label(self, text="Author:")
        self._entry_author = ttk.Entry(self, textvariable=self._author_var)

        self._label_copyright = ttk.Label(self, text="Copyright:")
        self._entry_copyright = ttk.Entry(self, textvariable=self._copyright_var)
        self._button_copyright = ttk.Button(self, text="©", command=self._on_copyright)

        self._label_city = ttk.Label(self, text="City:")
        self._entry_city = ttk.Entry(self, textvariable=self._city_var)

        self._label_sublocation = ttk.Label(self, text="Sublocation:")
        self._entry_sublocation = ttk.Entry(self, textvariable=self._sublocation_var)

        self._label_country = ttk.Label(self, text="Country:")
        self._combo_country = ShiftScrollCombobox(
            self,
            textvariable=self._country_var,
            values=[country for country, _ in COUNTRIES],
        )

        self._label_date_taken = ttk.Label(self, text="Date taken:")
        self._entry_date_taken = ValidatingEntry(
            self, textvariable=self._date_taken_var
        )
        self._entry_date_taken.set_command(
            lambda value: not value or date_taken_valid(str(value))
        )
        self._button_today = ttk.Button(self, text="Today", command=self._on_today)

        self._button_clear = ttk.Button(self, text="Clear", command=self._on_clear)

        self._layout()

    def _layout(self) -> None:
        # --- Author ---
        self._label_author.grid(row=0, column=0, sticky="w")
        self._entry_author.grid(row=0, column=1, columnspan=2, sticky="ew")

        # --- Copyright ---
        self._label_copyright.grid(row=1, column=0, sticky="w")
        self._entry_copyright.grid(row=1, column=1, sticky="ew")
        self._button_copyright.grid(row=1, column=2, sticky="ew", padx=PADDING_SMALL)

        # --- City ---
        self._label_city.grid(row=2, column=0, sticky="w")
        self._entry_city.grid(row=2, column=1, columnspan=2, sticky="ew")

        # --- Sublocation ---
        self._label_sublocation.grid(row=3, column=0, sticky="w")
        self._entry_sublocation.grid(row=3, column=1, columnspan=2, sticky="ew")

        # --- Country ---
        self._label_country.grid(row=4, column=0, sticky="w")
        self._combo_country.grid(row=4, column=1, columnspan=2, sticky="ew")

        # --- Date taken ---
        self._label_date_taken.grid(row=5, column=0, sticky="w")
        self._entry_date_taken.grid(row=5, column=1, sticky="ew")
        self._button_today.grid(row=5, column=2, sticky="ew", padx=PADDING_SMALL)

        # --- buttons ---
        self._button_clear.grid(row=6, column=0, sticky="w", padx=PADDING_SMALL)

        self.columnconfigure(1, weight=1)

    def _get_default_country(self) -> str:
        if (country := get_string_option("country")) and country in [
            country for country, _ in COUNTRIES
        ]:
            return str(country)

        return ""

    # --- Callbacks ---
    def _on_clear(self) -> None:
        self.clear()

    def _on_copyright(self) -> None:
        parts = ["©"]
        author = self.author
        if author:
            parts.append(str(datetime.now().year))
            parts.append(author)
        self._copyright_var.set(" ".join(parts))

    def _on_today(self) -> None:
        self._date_taken_var.set(_default_time())

    # --- Public methods ---
    @property
    def author(self) -> str:
        return self._author_var.get().strip()

    @property
    def copyright(self) -> str:
        return self._copyright_var.get().strip()

    @property
    def city(self) -> str:
        return self._city_var.get().strip()

    @property
    def sublocation(self) -> str:
        return self._sublocation_var.get().strip()

    @property
    def country(self) -> str:
        return self._country_var.get().strip()

    @property
    def date_taken(self) -> str:
        return self._date_taken_var.get().strip()

    def clear(self):
        self._author_var.set("")
        self._copyright_var.set("")
        self._city_var.set("")
        self._sublocation_var.set("")
        self._country_var.set("")
        self._date_taken_var.set("")


def _default_time() -> str:
    today = datetime.today().date()
    noon_time = time(12, 0, 0)

    return datetime.combine(today, noon_time).strftime("%Y:%m:%d %H:%M:%S")
