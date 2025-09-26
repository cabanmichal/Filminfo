import re
import unicodedata
from datetime import datetime
from fractions import Fraction


def parse_shutter_speed(shutter_speed: str) -> tuple[float, str]:
    pattern = r"^(\d+(?:\.\d+)?)$|^(1\/\d+)$"
    match = re.match(pattern, shutter_speed)
    if not match:
        raise ValueError("Invalid shutter speed format")
    number, fraction = match.groups()
    if number:
        value_float = float(number)
        value_str = str(Fraction(value_float).limit_denominator())
        return value_float, value_str
    elif fraction:
        value_float = float(Fraction(fraction))
        return value_float, fraction
    else:
        raise ValueError("Invalid shutter speed format")


def parse_focal_length(focal_length: str) -> list[float]:
    parts = (
        focal_length.replace(" ", "")
        .replace(" ", "")  # nbsp
        .replace("mm", "")
        .replace("–", "-")  # en-dash
        .replace("—", "-")  # em-dash
        .split("-")
    )
    if len(parts) == 2:
        try:
            start = float(parts[0])
            end = float(parts[1])
            if not (0 < start < end):
                raise ValueError(
                    "Focal lengths cannot be negative and must be ascending"
                )
            return [start, end]
        except (ValueError, TypeError) as err:
            raise ValueError("Incorrect focal lenght format") from err

    if len(parts) == 1:
        try:
            focal_length_value = float(parts[0])
            if focal_length_value <= 0:
                raise ValueError("Focal length cannot be negative")
            return [focal_length_value]
        except (ValueError, TypeError) as err:
            raise ValueError("Incorrect focal lenght format") from err

    raise ValueError("Incorrect focal lenght format")


def exif_date_time_to_iptc(
    exif_date_time: str, fmt: str = "%Y:%m:%d %H:%M:%S"
) -> tuple[str, str]:
    date_time = datetime.strptime(exif_date_time, fmt)
    iptc_date = date_time.strftime("%Y%m%d")
    iptc_time = date_time.strftime("%H%M%S")

    return iptc_date, iptc_time


def to_ascii(s: str) -> str:
    nfkd_form = unicodedata.normalize("NFKD", s)
    return nfkd_form.encode("ascii", "ignore").decode("ascii")
