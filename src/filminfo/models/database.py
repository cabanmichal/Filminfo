import json
from pathlib import Path

from filminfo.models.entities import Camera, Film, Lens
from filminfo.models.validators import database_valid


class DatabaseError(RuntimeError):
    pass


class Database:
    def __init__(self, filepath: Path):
        self.filepath = filepath.expanduser().resolve()
        self.films: list[Film] = []
        self.cameras: list[Camera] = []
        self.lenses: list[Lens] = []
        self.load()

    def load(self) -> None:
        try:
            if database_valid(self.filepath):
                with open(self.filepath, "r") as database:
                    data = json.load(database)

                    for film in data["films"]:
                        self.films.append(Film.from_dict(film))

                    for camera in data["cameras"]:
                        self.cameras.append(Camera.from_dict(camera))

                    for lens in data["lenses"]:
                        self.lenses.append(Lens.from_dict(lens))

                    self.films.sort()
                    self.cameras.sort()
                    self.lenses.sort()
        except Exception as err:
            raise DatabaseError("Error loading the database") from err

    def save(self) -> None:
        try:
            with open(self.filepath, "w") as database:
                data = {
                    "films": [item.to_dict() for item in self.films],
                    "cameras": [item.to_dict() for item in self.cameras],
                    "lenses": [item.to_dict() for item in self.lenses],
                }
                json.dump(data, database, indent=4)
        except Exception as err:
            raise DatabaseError("Error writing the database") from err

        self.reload()

    def reload(self) -> None:
        self.films.clear()
        self.cameras.clear()
        self.lenses.clear()
        self.load()

    def add_film(self, film: Film) -> None:
        films = set(self.films)
        films.add(film)
        self.films = sorted(films)

    def add_camera(self, camera: Camera) -> None:
        cameras = set(self.cameras)
        cameras.add(camera)
        self.cameras = sorted(cameras)

    def add_lens(self, lens: Lens) -> None:
        lenses = set(self.lenses)
        lenses.add(lens)
        self.lenses = sorted(lenses)

    def remove_film(self, film: Film) -> None:
        self.films = [item for item in self.films if item != film]

    def remove_camera(self, camera: Camera) -> None:
        self.cameras = [item for item in self.cameras if item != camera]

    def remove_lens(self, lens: Lens) -> None:
        self.lenses = [item for item in self.lenses if item != lens]
