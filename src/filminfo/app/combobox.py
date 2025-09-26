import tkinter as tk
from tkinter import ttk

from filminfo.app.types import AnyWidget


class ShiftScrollCombobox(ttk.Combobox):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        def _on_mousewheel(event: tk.Event) -> str | None:
            if int(event.state) & 0x0001:
                delta = 0
                if event.num == 4 or event.delta > 0:
                    delta = 1
                elif event.num == 5 or event.delta < 0:
                    delta = -1

                if (current := self.current()) == -1 and delta == -1:
                    current = 1

                new_index = (current + delta) % len(self["values"])
                self.current(new_index)

                self.event_generate("<<ComboboxSelected>>")

            return "break"

        for button in ["<MouseWheel>", "<Button-4>", "<Button-5>"]:
            self.bind(button, _on_mousewheel)
