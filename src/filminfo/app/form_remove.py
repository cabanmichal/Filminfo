import tkinter as tk
from tkinter import ttk

from filminfo.app.scrollable_frame import ScrollableFrame
from filminfo.app.treeview import CustomTreeview
from filminfo.app.types import AnyWidget
from filminfo.configuration import APP_NAME, PADDING_SMALL


class RemoveMetadaForm(ttk.Frame):
    def __init__(self, parent: AnyWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # --- Elements ---
        self._form_scrollable = ScrollableFrame(self, horizontal=False)
        self._check_tree = _CheckTree(self._form_scrollable.container)
        self._label_tags = ttk.Label(self, text="Tags:")
        self._button_expand = ttk.Button(
            self, text="Expand all", command=self._on_expand_all
        )
        self._button_collapse = ttk.Button(
            self, text="Collapse all", command=self._on_collapse_all
        )
        self._label_tags_other = ttk.Label(
            self,
            text=(
                "Other (comma separated):\nExample: EXIF:Software, XMP-xmp:CreatorTool"
            ),
        )
        self._text_tags_other = tk.Text(self, height=5, width=50)

        self._layout()
        self.__configure()

    def _layout(self) -> None:
        self._label_tags.grid(row=0, column=0, sticky="w")
        self._button_expand.grid(row=1, column=0, sticky="w", padx=(0, PADDING_SMALL))
        self._button_collapse.grid(row=1, column=1, sticky="w", padx=PADDING_SMALL)

        self._form_scrollable.grid(row=2, column=0, sticky="nsew", columnspan=3)
        self._check_tree.grid(row=0, column=0, sticky="nsew")

        self._label_tags_other.grid(row=3, column=0, sticky="w", columnspan=3)
        self._text_tags_other.grid(row=4, column=0, sticky="ew", columnspan=3)

        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)
        self._form_scrollable.container.columnconfigure(0, weight=1)
        self._form_scrollable.container.rowconfigure(0, weight=1)

    def __configure(self) -> None:
        app_name = APP_NAME.capitalize()
        items = [
            "/Groups/EXIF:ALL",
            "/Groups/IPTC:ALL",
            "/Groups/XMP:ALL",
            f"/{app_name}/Camera/Make/EXIF:Make",
            f"/{app_name}/Camera/Model/EXIF:Model",
            f"/{app_name}/Camera/Serial/EXIF:CameraSerialNumber",
            f"/{app_name}/Lens/Make/EXIF:LensMake",
            f"/{app_name}/Lens/Model/EXIF:LensModel",
            f"/{app_name}/Lens/Focal length/EXIF:FocalLength",
            f"/{app_name}/Lens/Focal length/EXIF:FocalLengthIn35mmFormat",
            f"/{app_name}/Lens/Serial/EXIF:LensSerialNumber",
            f"/{app_name}/Origin/Author/EXIF:Artist",
            f"/{app_name}/Origin/Author/IPTC:By-line",
            f"/{app_name}/Origin/Author/XMP-dc:Creator",
            f"/{app_name}/Origin/Copyright/EXIF:Copyright",
            f"/{app_name}/Origin/Copyright/IPTC:CopyrightNotice",
            f"/{app_name}/Origin/Copyright/XMP-dc:Rights",
            f"/{app_name}/Origin/Copyright/XMP-xmpRights:Marked",
            f"/{app_name}/Origin/City/IPTC:City",
            f"/{app_name}/Origin/City/XMP-photoshop:City",
            f"/{app_name}/Origin/City/XMP-iptcExt:LocationShownCity",
            f"/{app_name}/Origin/Sublocation/IPTC:Sub-location",
            f"/{app_name}/Origin/Sublocation/XMP-iptcCore:Location",
            f"/{app_name}/Origin/Sublocation/XMP-iptcExt:LocationShownSublocation",
            f"/{app_name}/Origin/Country/IPTC:Country-PrimaryLocaitonName",
            f"/{app_name}/Origin/Country/XMP-photoshop:Country",
            f"/{app_name}/Origin/Country/XMP-iptcExt:LocationShownCountryName",
            f"/{app_name}/Origin/Country code/IPTC:Country-PrimaryLocationCode",
            f"/{app_name}/Origin/Country code/XMP-iptcCore:CountryCode",
            f"/{app_name}/Origin/Country code/XMP-iptcExt:LocationCreatedCountryCode",
            f"/{app_name}/Origin/Date taken/EXIF:DateTimeOriginal",
            f"/{app_name}/Origin/Date taken/XMP-photoshop:DateCreated",
            f"/{app_name}/Origin/Date taken/IPTC:DateCreated",
            f"/{app_name}/Origin/Date taken/IPTC:TimeCreated",
            f"/{app_name}/Exposure/Aperture/EXIF:FNumber",
            f"/{app_name}/Exposure/Shutter speed/EXIF:ExposureTime",
            f"/{app_name}/Exposure/ISO/EXIF:ISO",
            f"/{app_name}/Comments/Description/EXIF:ImageDescription",
            f"/{app_name}/Comments/Description/IPTC:Caption-Abstract",
            f"/{app_name}/Comments/Comment/EXIF:UserComment",
            f"/{app_name}/Comments/Comment/XMP-dc:Description",
        ]
        for item in items:
            self._check_tree.add_item(item)

        self._check_tree.fit_content(width=400)

    def _on_collapse_all(self) -> None:
        self._check_tree.collapse_all()
        self._form_scrollable.scroll_to_top()

    def _on_expand_all(self) -> None:
        self._check_tree.expand_all()
        self._form_scrollable.scroll_to_top()

    @property
    def selected_items(self) -> list[str]:
        tags = self._check_tree.get_selected_leaves()
        other_tags = (
            self._text_tags_other.get("1.0", "end")
            .strip()
            .replace(" ", "")
            .replace(";", ",")
            .split(",")
        )
        tags.extend(other_tags)

        return tags


class _CheckTree(ttk.Frame):
    ICON_UNCHECKED = "□"
    ICON_CHECKED = "☑"
    ICON_PARTIAL = "▣"

    STATE_UNCHECKED = 0
    STATE_CHECKED = 1
    STATE_PARTIAL = 2

    STATE_ICON_MAP = {
        STATE_UNCHECKED: ICON_UNCHECKED,
        STATE_CHECKED: ICON_CHECKED,
        STATE_PARTIAL: ICON_PARTIAL,
    }

    def __init__(self, parent: AnyWidget, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self._height = 0
        self._states: dict[str, int] = {}

        self._tree = CustomTreeview(self, columns=(), show="tree", selectmode="none")
        self._tree.column("#0", stretch=True)
        self._tree.bind("<Button-1>", self._on_click, add="+")

        self._tree.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _remove_checkmarks(self, item: str) -> str:
        to_strip = "".join(
            [
                _CheckTree.ICON_UNCHECKED,
                _CheckTree.ICON_CHECKED,
                _CheckTree.ICON_PARTIAL,
                " ",
            ]
        )
        return item.lstrip(to_strip)

    def _set_state(self, item: str, state: int) -> None:
        self._states[item] = state
        label = self._remove_checkmarks(self._tree.item(item, "text"))
        symbol = _CheckTree.STATE_ICON_MAP[state]
        self._tree.item(item, text=f"{symbol} {label}")

    def _propagate_to_children(self, item: str, state: int) -> None:
        for child in self._tree.get_children(item):
            self._set_state(child, state)
            self._propagate_to_children(child, state)

    def _update_parent_state(self, item: str | None) -> None:
        if not item:
            return

        child_states = [self._states[c] for c in self._tree.get_children(item)]
        if all(s == _CheckTree.STATE_CHECKED for s in child_states):
            state = _CheckTree.STATE_CHECKED
        elif all(s == _CheckTree.STATE_UNCHECKED for s in child_states):
            state = _CheckTree.STATE_UNCHECKED
        else:
            state = _CheckTree.STATE_PARTIAL

        self._set_state(item, state)
        self._update_parent_state(self._tree.parent(item))

    # --- Callbacks ---
    def _on_click(self, event: tk.Event) -> None:
        element = self._tree.identify("element", event.x, event.y)
        if element != "text":
            return

        item = self._tree.identify_row(event.y)
        state = self._states.get(item, _CheckTree.STATE_UNCHECKED)
        if state == _CheckTree.STATE_CHECKED:
            new_state = _CheckTree.STATE_UNCHECKED
        else:
            new_state = _CheckTree.STATE_CHECKED

        self._set_state(item, new_state)
        self._propagate_to_children(item, new_state)
        self._update_parent_state(self._tree.parent(item))

    # --- Public methods ---
    def add_item(self, item: str, open: bool = False, separator: str = "/") -> None:
        parent, text = item.rsplit(separator, 1)
        if not parent or parent in self._states:
            self._tree.insert(
                parent,
                "end",
                text=f"{_CheckTree.ICON_UNCHECKED} {text}",
                open=open,
                iid=item,
            )
            self._states[item] = _CheckTree.STATE_UNCHECKED
        else:
            self.add_item(parent, open, separator)
            self.add_item(item, open, separator)

    def get_selected_leaves(self) -> list[str]:
        leaves = []
        for item, state in self._states.items():
            if state == _CheckTree.STATE_CHECKED and not self._tree.get_children(item):
                label = self._remove_checkmarks(self._tree.item(item, "text"))
                leaves.append(label)
        return leaves

    def expand_all(self, parent: str = "") -> None:
        self._tree.expand_all(parent)

    def collapse_all(self, parent: str = "") -> None:
        self._tree.collapse_all(parent)

    def fit_content(self, width: int) -> None:
        self._tree["height"] = len(self._states)
        self._tree.column("#0", width=width)
