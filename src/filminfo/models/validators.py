import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from filminfo.models.convertes import parse_focal_length, parse_shutter_speed


def _file_has_permissions(
    file_path: Path, permission: Literal["read", "write"]
) -> bool:
    if not file_path.exists():
        return False

    if not file_path.is_file():
        return False

    if not os.access(file_path, os.R_OK if permission == "read" else os.W_OK):
        return False

    return True


def file_readable(file_path: Path) -> bool:
    return _file_has_permissions(file_path, "read")


def file_writeable(file_path: Path) -> bool:
    return _file_has_permissions(file_path, "write")


def database_valid(path: str | Path) -> bool:
    try:
        with open(path, "r") as file:
            data = json.load(file)
            return all(
                isinstance(data.get(key), list)
                for key in ("films", "cameras", "lenses")
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def iso_valid(iso: str) -> bool:
    try:
        iso_value = int(iso)
    except (ValueError, TypeError):
        return False

    return iso_value > 0


def crop_valid(crop: str) -> bool:
    try:
        crop_value = float(crop)
    except (ValueError, TypeError):
        return False

    return crop_value > 0


def aperture_valid(aperture: str) -> bool:
    try:
        aperture_value = float(aperture)
    except (ValueError, TypeError):
        return False

    return aperture_value > 0


def focal_length_valid(focal_length: str) -> bool:
    try:
        _ = parse_focal_length(focal_length)
        return True
    except ValueError:
        return False


def shutter_speed_valid(shutter_speed: str) -> bool:
    try:
        _ = parse_shutter_speed(shutter_speed)
        return True
    except ValueError:
        return False


def date_taken_valid(date_time: str, fmt: str = "%Y:%m:%d %H:%M:%S") -> bool:
    try:
        datetime.strptime(date_time, fmt)
        return True
    except ValueError:
        return False


def resolution_valid(resolution: str) -> bool:
    try:
        aperture_value = float(resolution)
    except (ValueError, TypeError):
        return False

    return aperture_value > 0
