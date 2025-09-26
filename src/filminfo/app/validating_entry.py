from tkinter import ttk

from filminfo.app.types import AnyWidget, EntryCallback


class ValidatingEntry(ttk.Entry):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._default_style = "TEntry"
        self._error_style = "Invalid.TEntry"

    def set_command(self, command: EntryCallback) -> None:
        def on_validate(value: int | float | str) -> bool:
            if command(value):
                self.configure(style=self._default_style)
                return True
            else:
                self.configure(style=self._error_style)
                return False

        self.configure(
            validate="focusout",
            validatecommand=(self.register(on_validate), "%P"),
        )
