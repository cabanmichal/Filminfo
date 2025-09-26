import tkinter as tk
from collections.abc import Callable


ButtonCallback = Callable[[], None]
EntryCallback = Callable[[int | float | str], bool]
AnyWidget = tk.Misc
