import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

from filminfo.models.validators import database_valid, file_readable, file_writeable


__ALL__ = [
    "APP_NAME",
    "CONFIG_NAME",
    "DB_NAME",
    "DEFAULT_WIN_SIZE",
    "MIN_WIN_SIZE",
    "PADDING_SMALL",
    "PADDING_MEDIUM",
    "PADDING_BIG",
    "get_app_dir",
    "get_config_file",
    "get_database_file",
    "ensure_database",
    "load_config",
    "get_int_option",
    "get_string_option",
    "get_float_option",
    "get_exiftool",
]

APP_NAME = "filminfo"
CONFIG_NAME = "config.json"
DB_NAME = "database.json"

DEFAULT_WIN_SIZE = (1200, 800)
MIN_WIN_SIZE = (1050, 700)

PADDING_SMALL = 2
PADDING_MEDIUM = 5
PADDING_BIG = 10

ConfigOption = str | int | float | None
_config_options_provider: Callable[[str], ConfigOption] | None = None


_DEFAULT_CONFIG: dict[str, ConfigOption] = {
    "author": None,
    "country": None,
    "exiftool": "exiftool",
    "thumbnail_size": 120,
    "thumbnail_highlight_color": "#2b90fd",
    "preview_size": 900,
    "error_text_color": "#e63946",
    "tree_highlight_color": "#2b90fd",
    "theme": None,
}

_EMPTY_DATABASE: dict[str, list[Any]] = {
    "films": [],
    "cameras": [],
    "lenses": [],
}


def get_app_dir() -> Path:
    path = Path(user_config_dir(APP_NAME))
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_file() -> Path:
    file_path = get_app_dir() / CONFIG_NAME
    return file_path.expanduser().resolve()


def get_database_file() -> Path:
    file_path = get_app_dir() / DB_NAME
    return file_path.expanduser().resolve()


def _create_empty_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with open(database_path, "w") as database:
        json.dump(_EMPTY_DATABASE, database, indent=4)


def _create_default_config(config_path: Path) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as config:
        json.dump(_DEFAULT_CONFIG, config, indent=4)


def ensure_database() -> Path:
    database_path = get_database_file()

    if database_path.exists():
        if not file_readable(database_path):
            raise PermissionError(
                f"Database exists but is not readable: {database_path}"
            )
        if not file_writeable(database_path):
            raise PermissionError(
                f"Database exists but is not writeable: {database_path}"
            )
        if database_valid(database_path):
            return database_path

    try:
        _create_empty_database(database_path)
        return database_path
    except Exception as err:
        raise OSError(f"Failed to create database {database_path}") from err


def load_config() -> None:
    config_path = get_config_file()
    if not config_path.exists():
        try:
            _create_default_config(config_path)
        except Exception as err:
            raise OSError(f"Failed to create config file {config_path}") from err

    with open(config_path, "r") as config_file:
        config: dict[str, ConfigOption] = json.load(config_file)

    def provider(option: str) -> ConfigOption:
        return config.get(option)

    global _config_options_provider
    _config_options_provider = provider


def _get_config(option: str) -> ConfigOption:
    if not _config_options_provider:
        raise RuntimeError("Configuration is not loaded")

    return _config_options_provider(option)


def get_int_option(option: str) -> int:
    value = _get_config(option)
    if value is None:
        value = _DEFAULT_CONFIG[option]
    assert value is not None

    return int(value)


def get_string_option(option: str) -> str:
    value = _get_config(option) or _DEFAULT_CONFIG[option] or ""

    return str(value)


def get_float_option(option: str) -> float:
    value = _get_config(option)
    if value is None:
        value = _DEFAULT_CONFIG[option]
    assert value is not None

    return float(value)


def get_exiftool() -> Path:
    path = Path(get_string_option("exiftool")).expanduser()

    if absolute := shutil.which(path):
        return Path(absolute).resolve()

    return path.resolve()
