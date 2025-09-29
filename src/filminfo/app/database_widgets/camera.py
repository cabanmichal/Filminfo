import tkinter as tk
from tkinter import messagebox, ttk

from filminfo.app.combobox import ShiftScrollCombobox
from filminfo.app.database_widgets import save_database
from filminfo.app.types import AnyWidget
from filminfo.configuration import PADDING_MEDIUM, PADDING_SMALL
from filminfo.controllers.database_controller import DatabaseController
from filminfo.models.entities import Camera, CropFactor
from filminfo.models.validators import crop_valid


class CameraWidget(ttk.LabelFrame):
    def __init__(
        self, parent: AnyWidget, controller: DatabaseController, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self._controller = controller
        self._cameras = controller.get_cameras()

        # --- Variables ---
        self._camera_var = tk.StringVar()
        self._make_var = tk.StringVar()
        self._model_var = tk.StringVar()
        self._crop_var = tk.StringVar()
        self._serial_var = tk.StringVar()

        # --- Camera selection ---
        self._label_camera = ttk.Label(self, text="Saved:")
        self._combo_camera = ShiftScrollCombobox(
            self,
            textvariable=self._camera_var,
            values=self._get_camera_names(),
            state="readonly",
        )
        self._combo_camera.bind("<<ComboboxSelected>>", self._on_camera_select)
        self._button_remove = ttk.Button(self, text="Remove", command=self._on_remove)

        # --- Make ---
        self._label_make = ttk.Label(self, text="Make:")
        self._entry_make = ttk.Entry(self, textvariable=self._make_var)

        # --- Model ---
        self._label_model = ttk.Label(self, text="Model:")
        self._entry_model = ttk.Entry(self, textvariable=self._model_var)

        # --- Crop ---
        self._label_crop = ttk.Label(self, text="Crop:")
        self._combo_crop = ShiftScrollCombobox(
            self,
            textvariable=self._crop_var,
            values=[str(factor) for factor in CropFactor],
            validate="focusout",
            validatecommand=(self.register(self._crop_valid), "%P"),
        )
        self._combo_crop.current(0)

        # --- Serial number ---
        self._label_serial = ttk.Label(self, text="Serial:")
        self._entry_serial = ttk.Entry(self, textvariable=self._serial_var)

        # --- Buttons ---
        self._button_clear = ttk.Button(self, text="Clear", command=self._on_clear)
        self._button_add = ttk.Button(self, text="Add", command=self._on_add)

        self._layout()

    def _layout(self) -> None:
        # --- Camera selection ---
        self._label_camera.grid(row=0, column=0, sticky="w")
        self._combo_camera.grid(row=0, column=1, sticky="ew")
        self._button_remove.grid(row=0, column=2, padx=PADDING_SMALL)

        # --- Make ---
        self._label_make.grid(row=1, column=0, sticky="w")
        self._entry_make.grid(row=1, column=1, columnspan=2, sticky="ew")

        # --- Model ---
        self._label_model.grid(row=2, column=0, sticky="w")
        self._entry_model.grid(row=2, column=1, columnspan=2, sticky="ew")

        # --- Crop ---
        self._label_crop.grid(row=3, column=0, sticky="w")
        self._combo_crop.grid(row=3, column=1, columnspan=2, sticky="ew")

        # --- Serial ---
        self._label_serial.grid(row=4, column=0, sticky="w")
        self._entry_serial.grid(row=4, column=1, columnspan=2, sticky="ew")

        # --- buttons ---
        self._button_clear.grid(row=5, column=0, sticky="w")
        self._button_add.grid(row=5, column=2, sticky="e")

        self.columnconfigure(1, weight=1)

        for widget in self.winfo_children():
            widget.grid_configure(padx=PADDING_MEDIUM, pady=PADDING_SMALL)

    def _make_camera_name(self, camera: Camera) -> str:
        parts = [camera.make, camera.model]
        if camera.serial:
            parts.append(camera.serial)

        return " ".join(parts)

    def _get_camera_names(self) -> list[str]:
        return [self._make_camera_name(camera) for camera in self._cameras]

    def _get_camera(self) -> Camera | None:
        index = self._combo_camera.current()
        if index >= 0 and index < len(self._cameras):
            return self._cameras[index]

        return None

    def _crop_from_option(self, option: str) -> str:
        return option.strip().split(" ")[0]

    def _crop_to_option(self, crop: float) -> int:
        value = CropFactor.from_float(crop)
        if not value:
            return -1
        return self._combo_crop["values"].index(str(value))

    def _make_camera(self) -> Camera | None:
        make = self.make
        model = self.model
        crop_value = self.crop
        crop = float(crop_value) if crop_value else CropFactor.FULL_FRAME.as_float()
        serial = self.serial

        if not make or not model:
            messagebox.showerror("Error", "Make and Model cannot be empty.")
            return None

        return Camera(make, model, crop, serial)

    # --- Callbacks ---
    def _on_camera_select(self, event: tk.Event | None = None) -> None:
        camera = self._get_camera()
        if camera:
            self._make_var.set(camera.make)
            self._model_var.set(camera.model)
            self._combo_crop.current(self._crop_to_option(camera.crop))
            self._serial_var.set(camera.serial)

    def _crop_valid(self, crop: str) -> bool:
        crop = self._crop_from_option(crop)
        if not crop or crop_valid(crop):
            self._combo_crop.configure(style="TCombobox")
            return True
        else:
            self._combo_crop.configure(style="Invalid.TCombobox")
            return False

    def _on_remove(self) -> None:
        camera = self._get_camera()
        if camera:
            self._controller.remove_camera(camera)
            save_database(self._controller)
            self._cameras = self._controller.get_cameras()
            self._combo_camera["values"] = self._get_camera_names()

        self._camera_var.set("")

    def _on_add(self) -> None:
        camera = self._make_camera()
        if camera:
            self._controller.add_camera(camera)
            save_database(self._controller)
            self._cameras = self._controller.get_cameras()
            self._combo_camera["values"] = self._get_camera_names()
            self._camera_var.set(self._make_camera_name(camera))

    def _on_clear(self) -> None:
        self.clear()

    # --- Public methods ---
    @property
    def camera(self) -> str:
        return self._camera_var.get().strip()

    @property
    def make(self) -> str:
        return self._make_var.get().strip()

    @property
    def model(self) -> str:
        return self._model_var.get().strip()

    @property
    def crop(self) -> str:
        value = self._crop_from_option(self._crop_var.get())
        if crop_valid(value):
            return str(round(float(value), 2))
        return ""

    @property
    def serial(self) -> str:
        return self._serial_var.get().strip()

    @property
    def data(self) -> dict[str, str]:
        return {
            "camera_make": self.make,
            "camera_model": self.model,
            "camera_crop": self.crop,
            "camera_serial": self.serial,
        }

    def clear(self) -> None:
        self._camera_var.set("")
        self._make_var.set("")
        self._model_var.set("")
        self._crop_var.set("")
        self._serial_var.set("")
