import tkinter as tk
from tkinter import ttk

from filminfo.app.types import AnyWidget, ButtonCallback
from filminfo.configuration import PADDING_SMALL


class CommentWidget(ttk.LabelFrame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # --- Elements ---
        self._label_description = ttk.Label(self, text="Description:")
        self._text_description = tk.Text(self, height=1, width=50)

        self._label_user_comment = ttk.Label(self, text="User Comment:")
        self._text_user_comment = tk.Text(self, height=5, width=50)

        self._label_auto_comment = ttk.Label(self, text="Auto Comment:")
        self._text_auto_comment = tk.Text(self, height=5, width=50)

        self._button_refresh = ttk.Button(self, text="Refresh")
        self._button_clear = ttk.Button(self, text="Clear", command=self._on_clear)

        self._layout()

    def _layout(self) -> None:
        # --- Description ---
        self._label_description.grid(row=0, column=0, sticky="w")
        self._text_description.grid(row=1, column=0, columnspan=2, sticky="ew")

        # --- User comment ---
        self._label_user_comment.grid(row=2, column=0, sticky="w")
        self._text_user_comment.grid(row=3, column=0, columnspan=2, sticky="ew")

        # --- Auto comment ---
        self._label_auto_comment.grid(row=4, column=0, sticky="w")
        self._text_auto_comment.grid(row=5, column=0, columnspan=2, sticky="ew")

        # --- Buttons ---
        self._button_clear.grid(row=6, column=0, sticky="w", padx=PADDING_SMALL)
        self._button_refresh.grid(row=6, column=1, sticky="e", padx=PADDING_SMALL)

        self.columnconfigure(1, weight=1)

    # --- Callbacks ---
    def _on_clear(self) -> None:
        self.clear()

    # --- Public methods ---
    @property
    def description(self) -> str:
        return self._text_description.get("1.0", "end").strip()

    @property
    def user_comment(self) -> str:
        return self._text_user_comment.get("1.0", "end").strip()

    @property
    def auto_comment(self) -> str:
        return self._text_auto_comment.get("1.0", "end").strip()

    @auto_comment.setter
    def auto_comment(self, comment: str) -> None:
        self._text_auto_comment.delete("1.0", "end")
        self._text_auto_comment.insert("1.0", comment)

    @property
    def data(self) -> dict[str, str]:
        return {
            "comments_description": self.description,
            "comments_user_comment": self.user_comment,
            "comments_auto_comment": self.auto_comment,
        }

    def set_refresh_command(self, command: ButtonCallback) -> None:
        self._button_refresh.config(command=command)

    def clear(self) -> None:
        self._text_description.delete("1.0", "end")
        self._text_user_comment.delete("1.0", "end")
        self._text_auto_comment.delete("1.0", "end")
