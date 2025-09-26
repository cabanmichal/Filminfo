from pathlib import Path

from filminfo.models.database import Database, DatabaseError
from filminfo.models.entities import Camera, Film, Lens


DatabaseReply = Exception | None


class DatabaseController:
    def __init__(self, database: Path):
        self.load_database(database)

    def get_films(self) -> list[Film]:
        return [item for item in self.database.films]

    def get_cameras(self) -> list[Camera]:
        return [item for item in self.database.cameras]

    def get_lenses(self) -> list[Lens]:
        return [item for item in self.database.lenses]

    def add_film(self, film: Film) -> None:
        self.database.add_film(film)

    def add_camera(self, camera: Camera) -> None:
        self.database.add_camera(camera)

    def add_lens(self, lens: Lens) -> None:
        self.database.add_lens(lens)

    def remove_film(self, film: Film) -> None:
        self.database.remove_film(film)

    def remove_camera(self, camera: Camera) -> None:
        self.database.remove_camera(camera)

    def remove_lens(self, lens: Lens) -> None:
        self.database.remove_lens(lens)

    def save_database(self) -> DatabaseReply:
        try:
            self.database.save()
        except DatabaseError as err:
            return err

        return None

    def load_database(self, database: Path) -> DatabaseReply:
        try:
            self.database = Database(database)
        except DatabaseError as err:
            return err

        return None
