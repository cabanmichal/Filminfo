# <img width="50" alt="App icon" src="https://github.com/cabanmichal/Filminfo/raw/main/src/filminfo/assets/icon.png" /> Filminfo

Simple gui to add basic metadata to film scans.

-   You can store Film, Camera and Lens information and later reuse them.
-   Also allows to view and remove metadata from images.
-   Very basic support to export and re-import metadata.
-   Tested only on macOS (might work elsewhere).
-   Very few dependencies.
-   It uses [ExifTool](https://exiftool.org) to do the real work. It must be installed separately.

## How to use

### Add metadata

<img width="600" alt="Add metadata view" src="https://github.com/cabanmichal/Filminfo/raw/main/docs/images/01_add_metadata.webp" />

-   You can add images by pressing the `[Add images]` button or `<Command-o>`/`<Control-o>`.
-   `<Command-a>`/`<Control-a>` selects all images.
-   You can also select images using regular expression or clicking on the thumbnails.
-   `<Escape>` deselects all images.
-   `<asterisk>` inverts the selection.
-   `<Delete>` removes selected images.
-   Metadata are written to selected images by pressing the `[Execute]` button.

### Image preview

<img width="600" alt="Image preview" src="https://github.com/cabanmichal/Filminfo/raw/main/docs/images/02_preview.webp" />

-   Right clicks on a thumbnail opens and closes the preview.

### Remove metadata

<img width="600" alt="Remove metadata view" src="https://github.com/cabanmichal/Filminfo/raw/main/docs/images/03_remove_metadata.webp" />

-   Clicking on the indicators while holding `<Shift>` expands/collapses whole subtrees.
-   Metadata are removed from selected images by pressing the `[Execute]` button.

### View metadata

<img width="600" alt="View metadata view" src="https://github.com/cabanmichal/Filminfo/raw/main/docs/images/04_view_metadata.webp" />

-   Pressing the `[Execute]` button metadata of the selected images are loaded.
-   The metadata can be viewed in a separate window (press `[New window]`).

### Filter metadata

<img width="600" alt="Filter metadata view" src="https://github.com/cabanmichal/Filminfo/raw/main/docs/images/05_filter_metadata.webp" />

-   In the separate window metadata can be filtered using regular expression.
-   Double-click copies cell value to clipboard.

### Export/Import metadata

<img width="600" alt="Export/import metadata view" src="https://github.com/cabanmichal/Filminfo/raw/main/docs/images/06_export_import_metadata.webp" />

-   Some (predefined) tags can be exported to a json file.
-   This json file can be used to re-import the tags back.
-   Import only works when the images are in the same folder as the json. Doesn't work with subfolders.

## Installation

This is a python package. It requires python >= 3.12 and tkinter. One way to install the package:

```
git clone https://github.com/cabanmichal/Filminfo.git
cd Filminfo
pip install .
```

To run it:

```
python -m filminfo
```

## Attributions

Icon from: <a href="https://www.flaticon.com/free-icons/film-roll" title="film roll icons">Film roll icons created by Freepik - Flaticon</a>
