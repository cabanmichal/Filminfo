import tkinter as tk
from tkinter import messagebox, ttk

from filminfo.app.combobox import ShiftScrollCombobox
from filminfo.app.database_widgets import save_database
from filminfo.app.types import AnyWidget
from filminfo.app.validating_entry import ValidatingEntry
from filminfo.configuration import PADDING_SMALL
from filminfo.controllers.database_controller import DatabaseController
from filminfo.models.entities import Lens
from filminfo.models.validators import focal_length_valid


class LensWidget(ttk.LabelFrame):
    def __init__(
        self, parent: AnyWidget, controller: DatabaseController, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self._controller = controller
        self._lenses = controller.get_lenses()

        # --- Variables ---
        self._lens_var = tk.StringVar()
        self._make_var = tk.StringVar()
        self._model_var = tk.StringVar()
        self._fl_var = tk.StringVar()
        self._serial_var = tk.StringVar()

        # --- Lens selection ---
        self._label_lens = ttk.Label(self, text="Saved:")
        self._combo_lens = ShiftScrollCombobox(
            self,
            textvariable=self._lens_var,
            values=self._get_lens_names(),
            state="readonly",
        )
        self._combo_lens.bind("<<ComboboxSelected>>", self._on_combo_select)
        self._button_remove = ttk.Button(self, text="Remove", command=self._on_remove)

        # --- Make ---
        self._label_make = ttk.Label(self, text="Make:")
        self._entry_make = ttk.Entry(self, textvariable=self._make_var)

        # --- Model ---
        self._label_model = ttk.Label(self, text="Model:")
        self._entry_model = ttk.Entry(self, textvariable=self._model_var)

        # --- Focal length ---
        self._label_fl = ttk.Label(self, text="Focal length:")
        self._entry_fl = ValidatingEntry(self, textvariable=self._fl_var)
        self._entry_fl.set_command(
            lambda focal_length: not focal_length
            or focal_length_valid(str(focal_length))
        )

        # --- Serial number ---
        self._label_serial = ttk.Label(self, text="Serial:")
        self._entry_serial = ttk.Entry(self, textvariable=self._serial_var)

        # --- Buttons ---
        self._button_add = ttk.Button(self, text="Add", command=self._on_add)
        self._button_clear = ttk.Button(self, text="Clear", command=self._on_clear)

        self._layout()

    def _layout(self) -> None:
        # --- Lens selection ---
        self._label_lens.grid(row=0, column=0, sticky="w")
        self._combo_lens.grid(row=0, column=1, sticky="ew")
        self._button_remove.grid(row=0, column=2, padx=PADDING_SMALL)

        # --- Make ---
        self._label_make.grid(row=1, column=0, sticky="w")
        self._entry_make.grid(row=1, column=1, columnspan=2, sticky="ew")

        # --- Model ---
        self._label_model.grid(row=2, column=0, sticky="w")
        self._entry_model.grid(row=2, column=1, columnspan=2, sticky="ew")

        # --- Focal length ---
        self._label_fl.grid(row=3, column=0, sticky="w")
        self._entry_fl.grid(row=3, column=1, columnspan=2, sticky="ew")

        # --- Serial ---
        self._label_serial.grid(row=4, column=0, sticky="w")
        self._entry_serial.grid(row=4, column=1, columnspan=2, sticky="ew")

        # --- buttons ---
        self._button_clear.grid(row=5, column=0, sticky="w", padx=PADDING_SMALL)
        self._button_add.grid(row=5, column=2, sticky="e", padx=PADDING_SMALL)

        self.columnconfigure(1, weight=1)

    def _make_lens_name(self, lens: Lens) -> str:
        parts = [lens.make, lens.model]
        if lens.serial:
            parts.append(lens.serial)

        return " ".join(parts)

    def _get_lens_names(self) -> list[str]:
        return [self._make_lens_name(lens) for lens in self._lenses]

    def _get_lens(self) -> Lens | None:
        index = self._combo_lens.current()
        if index >= 0 and index < len(self._lenses):
            return self._lenses[index]

        return None

    def _make_lens(self) -> Lens | None:
        make = self.make
        model = self.model
        serial = self.serial

        if not make or not model:
            messagebox.showerror("Error", "Make and Model cannot be empty.")
            return None

        try:
            focal_length = [
                float(fl) for fl in self._fl_var.get().replace(" ", "").split("-")
            ]
        except ValueError:
            messagebox.showerror("Error", "Focal length must be a number.")
            return None

        return Lens(make, model, focal_length, serial)

    # --- Callbacks ---
    def _on_combo_select(self, event: tk.Event | None = None) -> None:
        lens = self._get_lens()
        if lens:
            self._make_var.set(lens.make)
            self._model_var.set(lens.model)
            self._fl_var.set(" - ".join(str(fl) for fl in lens.focal_length))
            self._serial_var.set(lens.serial)

    def _on_remove(self) -> None:
        lens = self._get_lens()
        if lens:
            self._controller.remove_lens(lens)
            save_database(self._controller)
            self._lenses = self._controller.get_lenses()
            self._combo_lens["values"] = self._get_lens_names()

        self._lens_var.set("")

    def _on_add(self) -> None:
        lens = self._make_lens()
        if lens:
            self._controller.add_lens(lens)
            save_database(self._controller)
            self._lenses = self._controller.get_lenses()
            self._combo_lens["values"] = self._get_lens_names()
            self._lens_var.set(self._make_lens_name(lens))

    def _on_clear(self) -> None:
        self.clear()

    # --- Public methods ---
    @property
    def lens(self) -> str:
        return self._lens_var.get().strip()

    @property
    def make(self) -> str:
        return self._make_var.get().strip()

    @property
    def model(self) -> str:
        return self._model_var.get().strip()

    @property
    def focal_length(self) -> str:
        return self._fl_var.get().strip()

    @property
    def serial(self) -> str:
        return self._serial_var.get().strip()

    def clear(self):
        self._lens_var.set("")
        self._make_var.set("")
        self._model_var.set("")
        self._fl_var.set("")
        self._serial_var.set("")
