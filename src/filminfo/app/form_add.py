from tkinter import ttk

from filminfo.app.comment import CommentWidget
from filminfo.app.database_widgets.camera import CameraWidget
from filminfo.app.database_widgets.film import FilmWidget
from filminfo.app.database_widgets.lens import LensWidget
from filminfo.app.exposure import ExposureWidget
from filminfo.app.origin import OriginWidget
from filminfo.app.other_tags import OtherTags
from filminfo.app.scrollable_frame import ScrollableFrame
from filminfo.app.types import AnyWidget
from filminfo.configuration import PADDING_SMALL
from filminfo.controllers.database_controller import DatabaseController


class AddMetadataForm(ttk.Frame):
    def __init__(
        self, parent: AnyWidget, db_controller: DatabaseController, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self._db_controller = db_controller

        self._form_scrollable = ScrollableFrame(self, horizontal=False)
        self._form_container = ttk.Frame(self._form_scrollable.container)

        # --- Elements ---
        self._film_widget = FilmWidget(self._form_container, db_controller, text="Film")
        self._camera_widget = CameraWidget(
            self._form_container, db_controller, text="Camera"
        )
        self._lens_widget = LensWidget(self._form_container, db_controller, text="Lens")
        self._origin_widget = OriginWidget(self._form_container, text="Origin")
        self._exposure_widget = ExposureWidget(self._form_container, text="Exposure")
        self._comment_widget = CommentWidget(self._form_container, text="Comments")
        self._other_tags_widget = OtherTags(self._form_container, text="Other")

        self._button_clear_all = ttk.Button(
            self, text="Clear all", command=self._on_clear
        )

        self._layout()
        self.__configure()

    def _layout(self) -> None:
        self._form_scrollable.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self._form_container.grid(row=0, column=0, sticky="nsew")

        self._film_widget.grid(row=0, column=0, sticky="ew", pady=PADDING_SMALL)
        self._camera_widget.grid(row=1, column=0, sticky="ew", pady=PADDING_SMALL)
        self._lens_widget.grid(row=2, column=0, sticky="ew", pady=PADDING_SMALL)
        self._origin_widget.grid(row=3, column=0, sticky="ew", pady=PADDING_SMALL)
        self._exposure_widget.grid(row=4, column=0, sticky="ew", pady=PADDING_SMALL)
        self._comment_widget.grid(row=5, column=0, sticky="ew", pady=PADDING_SMALL)
        self._other_tags_widget.grid(row=6, column=0, sticky="ew", pady=PADDING_SMALL)
        self._button_clear_all.grid(row=1, column=0, sticky="w", padx=PADDING_SMALL)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._form_scrollable.container.columnconfigure(0, weight=1)
        self._form_container.columnconfigure(0, weight=1)

    def __configure(self) -> None:
        self._comment_widget.set_refresh_command(self._on_refresh_auto_comment)
        self._exposure_widget.set_as_film_command(self._on_exposure_iso_as_film)

    # --- Callbacks ---
    def _on_clear(self) -> None:
        self.clear_all()

    def _on_exposure_iso_as_film(self) -> None:
        self._exposure_widget.iso = self._film_widget.iso

    def _on_refresh_auto_comment(self) -> None:
        parts = []
        camera_make = self._camera_widget.make
        camera_model = self._camera_widget.model
        if camera_make and camera_model:
            parts.append(f"Camera: {camera_make} {camera_model}")

        lens_make = self._lens_widget.make
        lens_model = self._lens_widget.model
        if lens_make and lens_model:
            parts.append(f"Lens: {lens_make} {lens_model}")

        film_make = self._film_widget.make
        film_name = self._film_widget.name
        if film_make and film_name:
            parts.append(f"Film: {film_make} {film_name}")

        parts.append("Sheet: ")

        comment = "\n".join(parts)
        if comment:
            self._comment_widget.auto_comment = comment

    # --- Public methods ---
    def clear_all(self) -> None:
        self._film_widget.clear()
        self._camera_widget.clear()
        self._lens_widget.clear()
        self._origin_widget.clear()
        self._exposure_widget.clear()
        self._comment_widget.clear()
        self._other_tags_widget.clear()

    @property
    def form_data(self) -> dict[str, str]:
        return {
            "film_make": self._film_widget.make,
            "film_name": self._film_widget.name,
            "film_iso": self._film_widget.iso,
            "film_format": self._film_widget.format,
            "camera_make": self._camera_widget.make,
            "camera_model": self._camera_widget.model,
            "camera_crop": str(self._camera_widget.crop),
            "camera_serial": self._camera_widget.serial,
            "lens_make": self._lens_widget.make,
            "lens_model": self._lens_widget.model,
            "lens_focal_length": self._lens_widget.focal_length,
            "lens_serial": self._lens_widget.serial,
            "origin_author": self._origin_widget.author,
            "origin_copyright": self._origin_widget.copyright,
            "origin_city": self._origin_widget.city,
            "origin_sublocation": self._origin_widget.sublocation,
            "origin_country": self._origin_widget.country,
            "origin_date_taken": self._origin_widget.date_taken,
            "exposure_aperture": self._exposure_widget.aperture,
            "exposure_shutter_speed": self._exposure_widget.shutter_speed,
            "exposure_iso": self._exposure_widget.iso,
            "comments_description": self._comment_widget.description,
            "comments_user_comment": self._comment_widget.user_comment,
            "comments_auto_comment": self._comment_widget.auto_comment,
            "other_resolution": self._other_tags_widget.resolution,
            "other_tags": ",".join(self._other_tags_widget.other_tags),
        }
