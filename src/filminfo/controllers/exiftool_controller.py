from collections.abc import Sequence
from pathlib import Path

from filminfo.models.exiftool import ExifTool, ExifToolReply


class ExifToolController:
    def __init__(self, exiftool: Path) -> None:
        self._exiftool = ExifTool(exiftool)

    def add_metadata(
        self, images: Sequence[str], metadata: dict[str, str]
    ) -> ExifToolReply:
        return self._exiftool.add_metadata(images, metadata)

    def remove_metadata(
        self, images: Sequence[str], tags: Sequence[str]
    ) -> ExifToolReply:
        return self._exiftool.remove_metadata(images, tags)

    def get_metadata(self, images: Sequence[str]) -> ExifToolReply:
        return self._exiftool.get_metadata(images)
